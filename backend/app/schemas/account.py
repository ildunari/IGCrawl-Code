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


class CredentialUpdate(BaseModel):
    password: str


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
    has_credentials: bool = False
    
    class Config:
        orm_mode = True
        
    @staticmethod
    def from_orm(account):
        response = AccountResponse(
            id=account.id,
            username=account.username,
            is_bookmarked=account.is_bookmarked,
            full_name=account.full_name,
            profile_pic_url=account.profile_pic_url,
            is_verified=account.is_verified,
            is_private=account.is_private,
            follower_count=account.follower_count,
            following_count=account.following_count,
            created_at=account.created_at,
            updated_at=account.updated_at,
            last_scraped=account.last_scraped,
            has_credentials=bool(account.encrypted_password)
        )
        return response