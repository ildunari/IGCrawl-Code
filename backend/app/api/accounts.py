from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ..database import get_session
from ..models import Account
from ..schemas.account import AccountCreate, AccountUpdate, AccountResponse

router = APIRouter()


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    bookmarked_only: bool = False,
    session: Session = Depends(get_session)
):
    """List all accounts with optional filtering"""
    query = select(Account)
    
    if search:
        query = query.where(Account.username.contains(search))
    
    if bookmarked_only:
        query = query.where(Account.is_bookmarked == True)
    
    query = query.offset(skip).limit(limit)
    accounts = session.exec(query).all()
    
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific account by ID"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account


@router.post("/", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    session: Session = Depends(get_session)
):
    """Create a new account to track"""
    # Check if account already exists
    existing = session.exec(
        select(Account).where(Account.username == account.username)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists")
    
    db_account = Account(**account.dict())
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    
    return db_account


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    session: Session = Depends(get_session)
):
    """Update an account"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = account_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
    
    account.updated_at = datetime.utcnow()
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    session: Session = Depends(get_session)
):
    """Delete an account and all related data"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    session.delete(account)
    session.commit()
    
    return {"message": "Account deleted successfully"}