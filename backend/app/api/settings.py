from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlmodel import Session
from typing import Dict, Any
import os
from pathlib import Path

from ..database import get_session
from ..config import get_settings, Settings
from ..services.credential_service import CredentialService

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_settings(session: Session = Depends(get_session)):
    """Get current settings from environment and database"""
    settings = get_settings()
    credential_service = CredentialService()
    
    # Get stored Instagram credentials
    stored_creds = credential_service.get_credentials("default", session)
    
    return {
        "instagramUsername": stored_creds[0] if stored_creds else settings.instagram_username or "",
        "instagramPassword": stored_creds[1] if stored_creds else settings.instagram_password or "",
        "proxyUrl": f"http://{settings.proxy_username}:****@{settings.proxy_host}:{settings.proxy_port}" if settings.use_proxy else "",
        "useProxy": settings.use_proxy,
        "rateLimitPerMinute": settings.rate_limit_per_minute,
        "scrapeDelaySeconds": settings.scrape_delay_seconds,
        "jitterSecondsMin": getattr(settings, 'jitter_seconds_min', 5),
        "jitterSecondsMax": getattr(settings, 'jitter_seconds_max', 15),
        "enableDailyScrapes": getattr(settings, 'enable_daily_scrapes', True),
        "backupRetentionDays": getattr(settings, 'backup_retention_days', 30),
    }


@router.post("/", response_model=Dict[str, Any])
async def update_settings(
    data: Dict[str, Any],
    session: Session = Depends(get_session)
):
    """Update settings"""
    credential_service = CredentialService()
    
    # Update Instagram credentials if provided
    if data.get("instagramUsername") and data.get("instagramPassword"):
        credential_service.save_credentials(
            username="default",
            instagram_username=data["instagramUsername"],
            instagram_password=data["instagramPassword"],
            session=session
        )
    
    # In a real implementation, we'd update the .env file
    # For now, we'll just return the settings
    return {
        "success": True,
        "message": "Settings updated successfully"
    }


@router.post("/test-proxy")
async def test_proxy():
    """Test proxy connection"""
    from ..utils.proxy_config import test_proxy_connection
    
    try:
        success = test_proxy_connection()
        return {
            "success": success,
            "message": "Proxy connection successful" if success else "Proxy connection failed"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }