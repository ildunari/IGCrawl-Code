from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

from ..database import get_session
from ..models import Scrape, Account, ScrapeStatus, ScrapeType
from ..schemas.scrape import ScrapeCreate, ScrapeResponse
from ..workers import queue, scrape_instagram_account
from ..workers.queue import redis_conn
from rq.job import Job

router = APIRouter()


@router.post("/", response_model=ScrapeResponse)
async def create_scrape(
    scrape: ScrapeCreate,
    session: Session = Depends(get_session)
):
    """Create a new scrape job"""
    # Verify account exists
    account = session.get(Account, scrape.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Create scrape record
    db_scrape = Scrape(
        account_id=scrape.account_id,
        scrape_type=scrape.scrape_type,
        status=ScrapeStatus.PENDING
    )
    session.add(db_scrape)
    session.commit()
    session.refresh(db_scrape)
    
    # Queue the job (use sync wrapper)
    from ..worker_wrapper import scrape_instagram_account as sync_scrape
    job = queue.enqueue(
        sync_scrape,
        scrape_id=db_scrape.id,
        username=account.username,
        scrape_type=scrape.scrape_type.value,
        use_private=scrape.use_private_creds
    )
    
    # Update scrape with job ID
    db_scrape.job_id = job.id
    session.add(db_scrape)
    session.commit()
    
    return db_scrape


@router.get("/{scrape_id}", response_model=ScrapeResponse)
async def get_scrape(
    scrape_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific scrape by ID"""
    scrape = session.get(Scrape, scrape_id)
    if not scrape:
        raise HTTPException(status_code=404, detail="Scrape not found")
    
    return scrape


@router.get("/progress/{job_id}")
async def scrape_progress(job_id: str):
    """Server-sent events for scrape progress"""
    async def event_generator():
        while True:
            # Get job status from Redis
            progress_key = f"scrape_progress_{job_id}"
            progress_data = redis_conn.get(progress_key)
            
            if progress_data:
                progress = json.loads(progress_data)
                yield {
                    "event": "progress",
                    "data": json.dumps(progress)
                }
                
                if progress.get("status") in ["completed", "failed"]:
                    break
            
            await asyncio.sleep(1)
    
    return EventSourceResponse(event_generator())


@router.get("/account/{account_id}", response_model=List[ScrapeResponse])
async def get_account_scrapes(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all scrapes for an account"""
    query = select(Scrape).where(Scrape.account_id == account_id)
    query = query.order_by(Scrape.started_at.desc())
    query = query.offset(skip).limit(limit)
    
    scrapes = session.exec(query).all()
    return scrapes


@router.post("/{scrape_id}/cancel", response_model=ScrapeResponse)
async def cancel_scrape(
    scrape_id: int,
    save_partial: bool = True,
    session: Session = Depends(get_session)
):
    """Cancel an ongoing scrape and optionally save partial results"""
    scrape = session.get(Scrape, scrape_id)
    if not scrape:
        raise HTTPException(status_code=404, detail="Scrape not found")
    
    if scrape.status not in [ScrapeStatus.PENDING, ScrapeStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel scrape with status: {scrape.status}"
        )
    
    # Cancel the job if it exists
    if scrape.job_id:
        try:
            job = Job.fetch(scrape.job_id, connection=redis_conn)
            job.cancel()
        except Exception as e:
            print(f"Error cancelling job: {e}")
    
    # Update scrape status
    scrape.status = ScrapeStatus.CANCELLED if not save_partial else ScrapeStatus.PARTIAL
    if save_partial:
        scrape.is_partial = True
        # Get current progress from Redis
        progress_key = f"scrape_progress_{scrape.job_id}"
        progress_data = redis_conn.get(progress_key)
        if progress_data:
            progress = json.loads(progress_data)
            scrape.followers_scraped = progress.get("followers_scraped", 0)
            scrape.following_scraped = progress.get("following_scraped", 0)
    
    scrape.completed_at = datetime.utcnow()
    session.add(scrape)
    session.commit()
    session.refresh(scrape)
    
    return scrape


@router.delete("/{scrape_id}")
async def delete_scrape(
    scrape_id: int,
    session: Session = Depends(get_session)
):
    """Delete a scrape and its associated data"""
    scrape = session.get(Scrape, scrape_id)
    if not scrape:
        raise HTTPException(status_code=404, detail="Scrape not found")
    
    # Only allow deletion of completed, failed, or cancelled scrapes
    if scrape.status in [ScrapeStatus.PENDING, ScrapeStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an ongoing scrape. Cancel it first."
        )
    
    session.delete(scrape)
    session.commit()
    
    return {"message": "Scrape deleted successfully"}