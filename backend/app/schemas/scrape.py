from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models import ScrapeStatus, ScrapeType


class ScrapeCreate(BaseModel):
    account_id: int
    scrape_type: ScrapeType
    use_private_creds: bool = False


class ScrapeResponse(BaseModel):
    id: int
    account_id: int
    scrape_type: ScrapeType
    status: ScrapeStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    followers_count: Optional[int]
    following_count: Optional[int]
    new_followers: Optional[int]
    lost_followers: Optional[int]
    error_message: Optional[str]
    job_id: Optional[str]
    
    class Config:
        orm_mode = True