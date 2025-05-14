from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FollowerResponse(BaseModel):
    target_id: int
    follower_id: int
    username: str
    full_name: Optional[str]
    profile_pic_url: Optional[str]
    is_verified: bool
    is_private: bool
    relation_type: str
    first_seen: datetime
    last_seen: datetime
    is_mutual: bool
    
    class Config:
        orm_mode = True