from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ..database import get_session
from ..models import Account
from ..schemas.account import AccountCreate, AccountUpdate, AccountResponse, CredentialUpdate
from ..services.credential_service import CredentialService

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
    
    return [AccountResponse.from_orm(account) for account in accounts]


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


@router.post("/{account_id}/credentials")
async def update_credentials(
    account_id: int,
    credentials: CredentialUpdate,
    session: Session = Depends(get_session)
):
    """Store Instagram credentials for an account"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Store credentials (automatically encrypted)
    success = CredentialService.store_credentials(
        username=account.username,
        password=credentials.password,
        session=session
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to store credentials")
    
    return {"message": "Credentials stored successfully"}


@router.delete("/{account_id}/credentials")
async def remove_credentials(
    account_id: int,
    session: Session = Depends(get_session)
):
    """Remove stored Instagram credentials"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    success = CredentialService.remove_credentials(
        username=account.username,
        session=session
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove credentials")
    
    return {"message": "Credentials removed successfully"}


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: int,
    session: Session = Depends(get_session)
):
    """Delete an account and all related data"""
    from ..models import Scrape, Follower
    
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        # First, delete all followers for all scrapes of this account
        scrapes = session.exec(select(Scrape).where(Scrape.account_id == account_id)).all()
        for scrape in scrapes:
            # Delete followers for this scrape
            followers = session.exec(select(Follower).where(Follower.scrape_id == scrape.id)).all()
            for follower in followers:
                session.delete(follower)
            # Delete the scrape itself
            session.delete(scrape)
        
        # Remove credentials if they exist
        try:
            if account.username:
                CredentialService.remove_credentials(
                    username=account.username,
                    session=session
                )
        except Exception:
            # Continue even if credentials removal fails
            pass
        
        # Finally delete the account
        session.delete(account)
        session.commit()
        
        # Return 204 No Content
        return None
    except Exception as e:
        session.rollback()
        # Log the error for debugging
        print(f"Error deleting account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete account: {str(e)}"
        )