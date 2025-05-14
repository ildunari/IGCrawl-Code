from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..utils.validators import validate_instagram_username


class AccountBase(BaseModel):
    username: str
    is_bookmarked: bool = False
    
    @validator('username')
    def validate_username(cls, v):
        if not validate_instagram_username(v):
            raise ValueError('Invalid Instagram username')
        return v.lower()


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    is_bookmarked: Optional[bool] = None


class AccountResponse(AccountBase):
    id: int
    full_name: Optional[str]
    profile_pic_url: Optional[str]
    is_verified: bool
    is_private: bool
    follower_count: Optional[int]
    following_count: Optional[int]
    created_at: datetime
    updated_at: datetime
    last_scraped: Optional[datetime]
    
    class Config:
        orm_mode = True