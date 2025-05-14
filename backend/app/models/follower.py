from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .scrape import Scrape


class FollowerRelationType(str):
    FOLLOWER = "follower"
    FOLLOWING = "following"


class Follower(SQLModel, table=True):
    """Follower/Following relationship data"""
    __tablename__ = "followers"
    
    # Composite primary key
    target_id: int = Field(primary_key=True)
    follower_id: int = Field(primary_key=True)
    scrape_id: int = Field(foreign_key="scrapes.id", primary_key=True)
    
    # Instagram user data
    username: str = Field(index=True)
    full_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_verified: bool = Field(default=False)
    is_private: bool = Field(default=False)
    
    # Relationship metadata
    relation_type: str  # 'follower' or 'following'
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    is_mutual: bool = Field(default=False)
    
    # Relationship tracking
    scrape: "Scrape" = Relationship(back_populates="followers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_id": 1,
                "follower_id": 12345,
                "scrape_id": 1,
                "username": "user123",
                "full_name": "John Doe",
                "is_verified": False,
                "relation_type": "follower"
            }
        }