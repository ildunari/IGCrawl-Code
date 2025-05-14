from typing import Dict, List, Optional
import json
import redis
import asyncio
from datetime import datetime
from sqlmodel import Session

from ..database import session_scope
from ..models import Scrape, Account, Follower, ScrapeStatus, FollowerRelationType
from ..scrapers import InstagramScraper
from ..config import get_settings
from .queue import redis_conn
from ..utils.rate_limiter import SlidingWindowRateLimiter

settings = get_settings()
rate_limiter = SlidingWindowRateLimiter()


def update_scrape_progress(job_id: str, progress: Dict, scrape_id: Optional[int] = None):
    """Update scrape progress in Redis for SSE"""
    if scrape_id:
        progress["scrape_id"] = scrape_id
    progress_key = f"scrape_progress_{job_id}"
    redis_conn.setex(progress_key, 300, json.dumps(progress))  # 5 minute TTL


async def scrape_instagram_account(
    scrape_id: int,
    username: str,
    scrape_type: str,
    use_private: bool = False
):
    """Worker task to scrape Instagram account"""
    job_id = None
    
    try:
        # Check rate limit before starting
        identifier = f"user:{username}"
        can_request, wait_time = rate_limiter.can_make_request(identifier)
        
        if not can_request:
            update_scrape_progress(job_id, {
                "status": "delayed",
                "message": f"Rate limited. Waiting {int(wait_time)} seconds...",
                "progress": 0,
                "retry_after": int(wait_time)
            }, scrape_id)
            await asyncio.sleep(wait_time)
        
        with session_scope() as session:
            # Get scrape record
            scrape = session.get(Scrape, scrape_id)
            if not scrape:
                raise ValueError(f"Scrape {scrape_id} not found")
            
            job_id = scrape.job_id
            
            # Update status to in progress
            scrape.status = ScrapeStatus.IN_PROGRESS
            scrape.started_at = datetime.utcnow()
            session.commit()
            
            # Update progress
            update_scrape_progress(job_id, {
                "status": "in_progress",
                "message": "Starting scrape...",
                "progress": 0
            }, scrape_id)
        
        # Record the request
        rate_limiter.record_request(identifier)
        
        # Initialize scraper with session
        with session_scope() as session:
            scraper = InstagramScraper(session)
        
        # Perform scrape based on type
        if scrape_type == "both":
            update_scrape_progress(job_id, {
                "status": "in_progress",
                "message": "Fetching followers and following...",
                "progress": 25
            }, scrape_id)
            
            data = await scraper.scrape_both(username, use_private)
            followers = data["followers"]
            following = data["following"]
            
        elif scrape_type == "followers":
            update_scrape_progress(job_id, {
                "status": "in_progress",
                "message": "Fetching followers...",
                "progress": 25
            }, scrape_id)
            
            followers = await scraper.scrape_followers(username, use_private)
            following = []
            
        else:  # following
            update_scrape_progress(job_id, {
                "status": "in_progress",
                "message": "Fetching following...",
                "progress": 25
            }, scrape_id)
            
            followers = []
            following = await scraper.scrape_following(username, use_private)
        
        # Process and save data
        with session_scope() as session:
            scrape = session.get(Scrape, scrape_id)
            account = session.get(Account, scrape.account_id)
            
            update_scrape_progress(job_id, {
                "status": "in_progress",
                "message": "Processing data...",
                "progress": 50
            }, scrape_id)
            
            # Create follower records
            follower_records = []
            
            # Process followers
            for f in followers:
                follower_records.append(Follower(
                    target_id=account.id,
                    follower_id=int(f["id"]),
                    scrape_id=scrape.id,
                    username=f["username"],
                    full_name=f.get("full_name"),
                    profile_pic_url=f.get("profile_pic_url"),
                    is_verified=f.get("is_verified", False),
                    is_private=f.get("is_private", False),
                    relation_type=FollowerRelationType.FOLLOWER
                ))
            
            # Process following
            following_ids = set()
            for f in following:
                following_ids.add(int(f["id"]))
                follower_records.append(Follower(
                    target_id=account.id,
                    follower_id=int(f["id"]),
                    scrape_id=scrape.id,
                    username=f["username"],
                    full_name=f.get("full_name"),
                    profile_pic_url=f.get("profile_pic_url"),
                    is_verified=f.get("is_verified", False),
                    is_private=f.get("is_private", False),
                    relation_type=FollowerRelationType.FOLLOWING
                ))
            
            # Mark mutuals
            for record in follower_records:
                if record.relation_type == FollowerRelationType.FOLLOWER:
                    if record.follower_id in following_ids:
                        record.is_mutual = True
            
            # Calculate delta from previous scrape
            from .delta_calculator import update_scrape_delta
            update_scrape_delta(session, scrape.id)
            
            update_scrape_progress(job_id, {
                "status": "in_progress",
                "message": "Saving to database...",
                "progress": 75
            }, scrape_id)
            
            # Bulk insert followers
            session.bulk_save_objects(follower_records)
            
            # Update scrape results
            scrape.followers_count = len(followers)
            scrape.following_count = len(following)
            scrape.status = ScrapeStatus.COMPLETED
            scrape.completed_at = datetime.utcnow()
            
            # Update account stats
            account.follower_count = len(followers)
            account.following_count = len(following)
            account.last_scraped = datetime.utcnow()
            
            session.commit()
            
            update_scrape_progress(job_id, {
                "status": "completed",
                "message": "Scrape completed successfully",
                "progress": 100,
                "results": {
                    "followers_count": len(followers),
                    "following_count": len(following)
                }
            }, scrape_id)
            
    except Exception as e:
        with session_scope() as session:
            scrape = session.get(Scrape, scrape_id)
            if scrape:
                scrape.status = ScrapeStatus.FAILED
                scrape.error_message = str(e)
                scrape.completed_at = datetime.utcnow()
                session.commit()
        
        if job_id:
            update_scrape_progress(job_id, {
                "status": "failed",
                "message": f"Scrape failed: {str(e)}",
                "progress": 0
            }, scrape_id)
        
        raise