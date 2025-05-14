from typing import Dict, List, Optional
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes
import time
import asyncio
from ..config import get_settings
from ..utils.crypto import decrypt_credential
from .graphql_scraper import GraphQLScraper

settings = get_settings()


class InstagramScraper:
    """Main Instagram scraper with GraphQL + instagrapi fallback"""
    
    def __init__(self):
        self.graphql_scraper = GraphQLScraper()
        self.private_client = None
        self.is_authenticated = False
        
    async def initialize_private_client(self):
        """Initialize instagrapi client for private accounts"""
        if not settings.instagram_username or not settings.instagram_password:
            return False
            
        try:
            self.private_client = Client()
            
            # Decrypt credentials
            username = decrypt_credential(settings.instagram_username)
            password = decrypt_credential(settings.instagram_password)
            
            # Login
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
        
        # Try GraphQL first
        try:
            followers = await self.graphql_scraper.get_all_followers(username)
            if followers:
                return followers
        except Exception as e:
            print(f"GraphQL scraper failed: {e}")
        
        # Fallback to instagrapi if needed or requested
        if use_private or not followers:
            if not self.is_authenticated:
                await self.initialize_private_client()
            
            if self.private_client:
                try:
                    user_id = self.private_client.user_id_from_username(username)
                    followers_raw = self.private_client.user_followers(user_id)
                    followers = [
                        self.standardize_user_data(f.dict(), "instagrapi") 
                        for f in followers_raw
                    ]
                except PleaseWaitFewMinutes:
                    print("Rate limited, waiting...")
                    await asyncio.sleep(60)
                except Exception as e:
                    print(f"Instagrapi scraper failed: {e}")
        
        return followers
    
    async def scrape_following(self, username: str, use_private: bool = False) -> List[Dict]:
        """Scrape following with GraphQL first, fallback to instagrapi"""
        following = []
        
        # Try GraphQL first
        try:
            following = await self.graphql_scraper.get_all_following(username)
            if following:
                return following
        except Exception as e:
            print(f"GraphQL scraper failed: {e}")
        
        # Fallback to instagrapi if needed or requested
        if use_private or not following:
            if not self.is_authenticated:
                await self.initialize_private_client()
            
            if self.private_client:
                try:
                    user_id = self.private_client.user_id_from_username(username)
                    following_raw = self.private_client.user_following(user_id)
                    following = [
                        self.standardize_user_data(f.dict(), "instagrapi") 
                        for f in following_raw
                    ]
                except PleaseWaitFewMinutes:
                    print("Rate limited, waiting...")
                    await asyncio.sleep(60)
                except Exception as e:
                    print(f"Instagrapi scraper failed: {e}")
        
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