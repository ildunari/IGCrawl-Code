from sqlmodel import Session, select
from typing import Set, Tuple
from ..models import Scrape, Follower


def calculate_follower_delta(
    session: Session,
    account_id: int,
    current_scrape_id: int
) -> Tuple[Set[int], Set[int]]:
    """
    Calculate new and lost followers compared to the previous scrape
    Returns: (new_follower_ids, lost_follower_ids)
    """
    # Get the previous completed scrape
    previous_scrape = session.exec(
        select(Scrape)
        .where(
            Scrape.account_id == account_id,
            Scrape.id < current_scrape_id,
            Scrape.status == "completed"
        )
        .order_by(Scrape.completed_at.desc())
        .limit(1)
    ).first()
    
    if not previous_scrape:
        # No previous scrape, all followers are new
        current_followers = session.exec(
            select(Follower.follower_id)
            .where(
                Follower.scrape_id == current_scrape_id,
                Follower.relation_type == "follower"
            )
        ).all()
        return set(current_followers), set()
    
    # Get follower IDs from both scrapes
    previous_followers = set(session.exec(
        select(Follower.follower_id)
        .where(
            Follower.scrape_id == previous_scrape.id,
            Follower.relation_type == "follower"
        )
    ).all())
    
    current_followers = set(session.exec(
        select(Follower.follower_id)
        .where(
            Follower.scrape_id == current_scrape_id,
            Follower.relation_type == "follower"
        )
    ).all())
    
    # Calculate differences
    new_followers = current_followers - previous_followers
    lost_followers = previous_followers - current_followers
    
    return new_followers, lost_followers


def update_scrape_delta(
    session: Session,
    scrape_id: int
):
    """Update scrape record with delta calculations"""
    scrape = session.get(Scrape, scrape_id)
    if not scrape:
        return
    
    new_follower_ids, lost_follower_ids = calculate_follower_delta(
        session,
        scrape.account_id,
        scrape_id
    )
    
    scrape.new_followers = len(new_follower_ids)
    scrape.lost_followers = len(lost_follower_ids)
    
    # Mark new followers in the follower table
    if new_follower_ids:
        session.exec(
            select(Follower)
            .where(
                Follower.scrape_id == scrape_id,
                Follower.follower_id.in_(new_follower_ids)
            )
        ).update({"is_new": True})
    
    session.commit()