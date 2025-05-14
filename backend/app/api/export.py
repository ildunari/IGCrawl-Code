from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from sqlmodel import Session, select
import pandas as pd
import io
import json
from typing import List, Literal
from datetime import datetime

from ..database import get_session
from ..models import Account, Scrape, Follower
from ..config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/{account_id}/followers")
async def export_followers(
    account_id: int,
    format: Literal["csv", "xlsx", "json"] = "csv",
    scrape_id: int = None,
    filter_type: Literal["all", "followers", "following", "mutuals"] = "all",
    session: Session = Depends(get_session)
):
    """Export followers/following data"""
    # Verify account exists
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Build query
    query = select(Follower).where(Follower.target_id == account_id)
    
    if scrape_id:
        query = query.where(Follower.scrape_id == scrape_id)
    else:
        # Get latest scrape
        latest_scrape = session.exec(
            select(Scrape)
            .where(Scrape.account_id == account_id)
            .order_by(Scrape.completed_at.desc())
            .limit(1)
        ).first()
        
        if latest_scrape:
            query = query.where(Follower.scrape_id == latest_scrape.id)
    
    # Apply filter
    if filter_type == "followers":
        query = query.where(Follower.relation_type == "follower")
    elif filter_type == "following":
        query = query.where(Follower.relation_type == "following")
    elif filter_type == "mutuals":
        query = query.where(Follower.is_mutual == True)
    
    # Get data
    followers = session.exec(query).all()
    
    # Convert to DataFrame
    data = []
    for f in followers:
        data.append({
            "username": f.username,
            "full_name": f.full_name,
            "is_verified": f.is_verified,
            "is_private": f.is_private,
            "relation_type": f.relation_type,
            "is_mutual": f.is_mutual,
            "first_seen": f.first_seen.isoformat(),
            "last_seen": f.last_seen.isoformat()
        })
    
    df = pd.DataFrame(data)
    
    # Export based on format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{account.username}_{filter_type}_{timestamp}"
    
    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.csv"
            }
        )
    
    elif format == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Add metadata sheet
            metadata = pd.DataFrame([{
                "Account": account.username,
                "Export Date": datetime.now().isoformat(),
                "Filter Type": filter_type,
                "Total Records": len(df)
            }])
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.xlsx"
            }
        )
    
    else:  # json
        return {
            "account": account.username,
            "export_date": datetime.now().isoformat(),
            "filter_type": filter_type,
            "total_records": len(data),
            "data": data
        }


@router.get("/{account_id}/analytics")
async def export_analytics(
    account_id: int,
    session: Session = Depends(get_session)
):
    """Export analytics data for an account"""
    # Verify account exists
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get all scrapes
    scrapes = session.exec(
        select(Scrape)
        .where(Scrape.account_id == account_id)
        .order_by(Scrape.completed_at.desc())
    ).all()
    
    # Build analytics data
    analytics = {
        "account": {
            "username": account.username,
            "is_verified": account.is_verified,
            "current_followers": account.follower_count,
            "current_following": account.following_count
        },
        "scrape_history": [],
        "growth_metrics": {
            "follower_growth": [],
            "following_growth": []
        }
    }
    
    for scrape in scrapes:
        analytics["scrape_history"].append({
            "date": scrape.completed_at.isoformat() if scrape.completed_at else None,
            "followers_count": scrape.followers_count,
            "following_count": scrape.following_count,
            "new_followers": scrape.new_followers,
            "lost_followers": scrape.lost_followers
        })
        
        if scrape.completed_at:
            analytics["growth_metrics"]["follower_growth"].append({
                "date": scrape.completed_at.isoformat(),
                "count": scrape.followers_count
            })
            analytics["growth_metrics"]["following_growth"].append({
                "date": scrape.completed_at.isoformat(),
                "count": scrape.following_count
            })
    
    return analytics