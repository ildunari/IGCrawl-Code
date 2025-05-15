from typing import Dict, List, Optional
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes
import time
import asyncio
import os
import urllib3
from ..config import get_settings
from ..services.credential_service import CredentialService
from .graphql_scraper import GraphQLScraper
from ..utils.proxy_config import configure_instagrapi_proxy
from sqlmodel import Session

# Disable SSL warnings when using proxies
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

settings = get_settings()


class InstagramScraper:
    """Main Instagram scraper with GraphQL + instagrapi fallback"""
    
    def __init__(self, session: Optional[Session] = None):
        self.graphql_scraper = GraphQLScraper()
        self.private_client = None
        self.is_authenticated = False
        self.session = session
        self.credential_service = CredentialService()
        
    async def initialize_private_client(self, username: str):
        """Initialize instagrapi client for private accounts using stored credentials"""
        if not self.session:
            return False
            
        # Get credentials from credential service
        credentials = self.credential_service.get_credentials(username, self.session)
        if not credentials:
            # Try with environment variables as fallback
            if not settings.instagram_username or not settings.instagram_password:
                return False
            credentials = (settings.instagram_username, settings.instagram_password)
            
        try:
            self.private_client = Client()
            
            # Configure proxy if enabled
            configure_instagrapi_proxy(self.private_client)
            
            # Login using the credentials
            username, password = credentials
            self.private_client.login(username, password)
            self.is_authenticated = True
            return True
        except Exception as e:
            print(f"Failed to initialize private client: {e}")
            return False
    
    def standardize_user_data(self, user: Dict, source: str = "graphql") -> Dict:
        """Standardize user data from different sources"""
        if source == "graphql":
            return user
        else:  # instagrapi format
            return {
                "id": str(user.get("pk", user.get("id", ""))),
                "username": user.get("username", ""),
                "full_name": user.get("full_name", ""),
                "profile_pic_url": user.get("profile_pic_url", ""),
                "is_verified": user.get("is_verified", False),
                "is_private": user.get("is_private", False)
            }
    
    async def scrape_followers(self, username: str, use_private: bool = False) -> List[Dict]:
        """Scrape followers with GraphQL first, fallback to instagrapi"""
        followers = []
        
        print(f"Starting follower scrape for {username} (use_private: {use_private})")
        
        # Try GraphQL first
        try:
            print(f"Trying GraphQL scraper for {username}")
            followers = await self.graphql_scraper.get_all_followers(username)
            print(f"GraphQL returned {len(followers)} followers")
            if followers:
                return followers
        except Exception as e:
            print(f"GraphQL scraper failed for {username}: {e}")
        
        # Fallback to instagrapi if needed or requested
        if use_private or not followers:
            print(f"Using private client for {username}")
            if not self.is_authenticated:
                print(f"Initializing private client for {username}")
                success = await self.initialize_private_client(username)
                print(f"Private client initialization result: {success}")
            
            if self.private_client:
                try:
                    print(f"Getting user ID for {username}")
                    user_id = self.private_client.user_id_from_username(username)
                    print(f"User ID: {user_id}")
                    followers_raw = self.private_client.user_followers(user_id)
                    print(f"Retrieved {len(followers_raw)} followers from instagrapi")
                    followers = [
                        self.standardize_user_data(f.dict(), "instagrapi") 
                        for f in followers_raw
                    ]
                except PleaseWaitFewMinutes:
                    print("Rate limited, waiting...")
                    await asyncio.sleep(60)
                except Exception as e:
                    print(f"Instagrapi scraper failed: {e}")
            else:
                print("Private client is not available")
        
        print(f"Returning {len(followers)} followers for {username}")
        return followers
    
    async def scrape_following(self, username: str, use_private: bool = False) -> List[Dict]:
        """Scrape following with GraphQL first, fallback to instagrapi"""
        following = []
        
        print(f"Starting following scrape for {username} (use_private: {use_private})")
        
        # Try GraphQL first
        try:
            print(f"Trying GraphQL scraper for following of {username}")
            following = await self.graphql_scraper.get_all_following(username)
            print(f"GraphQL returned {len(following)} following")
            if following:
                return following
        except Exception as e:
            print(f"GraphQL scraper failed for following: {e}")
        
        # Fallback to instagrapi if needed or requested
        if use_private or not following:
            print(f"Using private client for following of {username}")
            if not self.is_authenticated:
                print(f"Initializing private client for {username}")
                success = await self.initialize_private_client(username)
                print(f"Private client initialization result: {success}")
            
            if self.private_client:
                try:
                    print(f"Getting user ID for {username}")
                    user_id = self.private_client.user_id_from_username(username)
                    print(f"User ID: {user_id}")
                    following_raw = self.private_client.user_following(user_id)
                    print(f"Retrieved {len(following_raw)} following from instagrapi")
                    following = [
                        self.standardize_user_data(f.dict(), "instagrapi") 
                        for f in following_raw
                    ]
                except PleaseWaitFewMinutes:
                    print("Rate limited, waiting...")
                    await asyncio.sleep(60)
                except Exception as e:
                    print(f"Instagrapi scraper failed for following: {e}")
            else:
                print("Private client is not available")
        
        print(f"Returning {len(following)} following for {username}")
        return following
    
    async def scrape_both(self, username: str, use_private: bool = False) -> Dict[str, List[Dict]]:
        """Scrape both followers and following"""
        from ..utils.rate_limiter import SlidingWindowRateLimiter
        
        rate_limiter = SlidingWindowRateLimiter()
        
        # Add delay with jitter between requests
        followers = await self.scrape_followers(username, use_private)
        delay = rate_limiter.get_delay_with_jitter()
        await asyncio.sleep(delay)
        following = await self.scrape_following(username, use_private)
        
        return {
            "followers": followers,
            "following": following
        }