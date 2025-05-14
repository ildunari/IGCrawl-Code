from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .account import Account
    from .follower import Follower


class ScrapeStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class ScrapeType(str, Enum):
    FOLLOWERS = "followers"
    FOLLOWING = "following"
    BOTH = "both"


class Scrape(SQLModel, table=True):
    """Individual scrape run"""
    __tablename__ = "scrapes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)
    
    # Scrape details
    scrape_type: ScrapeType
    status: ScrapeStatus = Field(default=ScrapeStatus.PENDING)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    new_followers: Optional[int] = None
    lost_followers: Optional[int] = None
    
    # Progress tracking for partial saves
    followers_scraped: Optional[int] = None
    following_scraped: Optional[int] = None
    is_partial: bool = Field(default=False)
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = Field(default=0)
    
    # Job tracking
    job_id: Optional[str] = None
    
    # Relationships
    account: "Account" = Relationship(back_populates="scrapes")
    followers: List["Follower"] = Relationship(back_populates="scrape", cascade_delete=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_id": 1,
                "scrape_type": "both",
                "status": "completed",
                "followers_count": 1500,
                "following_count": 300
            }
        }