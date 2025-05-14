import schedule
import time
import threading
from datetime import datetime
from sqlmodel import Session, select

from ..database import session_scope
from ..models import Account, Scrape, ScrapeType
from .queue import queue
from .tasks import scrape_instagram_account
from ..config import get_settings

settings = get_settings()


def scheduled_scrape():
    """Run scheduled scrapes for bookmarked accounts"""
    with session_scope() as session:
        # Get all bookmarked accounts
        bookmarked_accounts = session.exec(
            select(Account).where(Account.is_bookmarked == True)
        ).all()
        
        for account in bookmarked_accounts:
            # Create a new scrape record
            scrape = Scrape(
                account_id=account.id,
                scrape_type=ScrapeType.BOTH,
                status="pending"
            )
            session.add(scrape)
            session.flush()  # Get the ID
            
            # Queue the scrape job (use sync wrapper)
            from ..worker_wrapper import scrape_instagram_account as sync_scrape
            job = queue.enqueue(
                sync_scrape,
                scrape_id=scrape.id,
                username=account.username,
                scrape_type="both",
                use_private=True  # Use private creds for scheduled scrapes
            )
            
            scrape.job_id = job.id
            session.commit()
            
            print(f"Scheduled scrape for {account.username} - Job ID: {job.id}")


def run_scheduler():
    """Run the scheduler in a separate thread"""
    # Schedule daily scrapes at 2:00 AM
    schedule.every().day.at("02:00").do(scheduled_scrape)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def start_scheduler():
    """Start the scheduler in a background thread"""
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    print("Scheduler started - Daily scrapes at 02:00")