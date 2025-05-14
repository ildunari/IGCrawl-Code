from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime


class Account(SQLModel, table=True):
    """Instagram account being tracked"""
    __tablename__ = "accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_verified: bool = Field(default=False)
    is_private: bool = Field(default=False)
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    
    # Authentication (encrypted)
    encrypted_password: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_scraped: Optional[datetime] = None
    is_bookmarked: bool = Field(default=False)
    
    # Relationships
    scrapes: List["Scrape"] = Relationship(back_populates="account", cascade_delete=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "instagram",
                "full_name": "Instagram",
                "is_verified": True,
                "follower_count": 500000000
            }
        }