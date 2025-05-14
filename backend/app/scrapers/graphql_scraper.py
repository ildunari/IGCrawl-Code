import httpx
from typing import Dict, List, Optional
import json
import re
import os
from ..utils.crypto import decrypt_credential
from ..config import get_settings
from ..utils.proxy_config import get_proxy_config


class GraphQLScraper:
    """Instagram GraphQL scraper for public accounts"""
    
    BASE_URL = "https://www.instagram.com/graphql/query/"
    FOLLOWERS_HASH = "5aefa9893005572d237da5068082d8d5"  # Instagram's query hash for followers
    FOLLOWING_HASH = "6df9f20c4ad9b22fb7b35b816f0c426e"  # Instagram's query hash for following
    
    def __init__(self):
        # Prepare httpx client arguments
        client_args = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "X-Requested-With": "XMLHttpRequest"
            }
        }
        
        # Add proxy configuration
        proxy_config = get_proxy_config()
        client_args.update(proxy_config)
        
        if proxy_config:
            print(f"GraphQL using proxy configuration: {proxy_config.get('proxies', {})}")
            if proxy_config.get('verify'):
                print(f"Using SSL certificate: {proxy_config.get('verify')}")
        
        self.session = httpx.Client(**client_args)
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username"""
        try:
            url = f"https://www.instagram.com/{username}/"
            print(f"Fetching Instagram page for user: {url}")
            response = self.session.get(url)
            print(f"Response status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Non-200 status code: {response.status_code}")
                return None
            
            # Extract user ID from page content
            content = response.text
            print(f"Response content length: {len(content)}")
            user_id_match = re.search(r'"profilePage_([0-9]+)"', content)
            if user_id_match:
                user_id = user_id_match.group(1)
                print(f"Found user ID: {user_id}")
                return user_id
            else:
                print("Could not find user ID in page content")
            
            return None
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None
    
    async def fetch_followers(self, user_id: str, limit: int = 100, after: Optional[str] = None) -> Dict:
        """Fetch followers for a user"""
        variables = {
            "id": user_id,
            "first": limit,
            "after": after
        }
        
        params = {
            "query_hash": self.FOLLOWERS_HASH,
            "variables": json.dumps(variables)
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            return response.json()
        except Exception as e:
            print(f"Error fetching followers: {e}")
            return {}
    
    async def fetch_following(self, user_id: str, limit: int = 100, after: Optional[str] = None) -> Dict:
        """Fetch following for a user"""
        variables = {
            "id": user_id,
            "first": limit,
            "after": after
        }
        
        params = {
            "query_hash": self.FOLLOWING_HASH,
            "variables": json.dumps(variables)
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            return response.json()
        except Exception as e:
            print(f"Error fetching following: {e}")
            return {}
    
    def parse_user_data(self, node: Dict) -> Dict:
        """Parse user data from GraphQL response"""
        return {
            "id": node.get("id"),
            "username": node.get("username"),
            "full_name": node.get("full_name"),
            "profile_pic_url": node.get("profile_pic_url"),
            "is_verified": node.get("is_verified", False),
            "is_private": node.get("is_private", False)
        }
    
    async def get_all_followers(self, username: str) -> List[Dict]:
        """Get all followers for a username"""
        print(f"Getting user ID for {username} in GraphQL")
        user_id = await self.get_user_id(username)
        print(f"User ID from GraphQL: {user_id}")
        if not user_id:
            print(f"Failed to get user ID for {username}")
            return []
        
        followers = []
        after = None
        
        while True:
            data = await self.fetch_followers(user_id, after=after)
            
            if not data or "data" not in data:
                break
            
            edges = data["data"]["user"]["edge_followed_by"]["edges"]
            for edge in edges:
                followers.append(self.parse_user_data(edge["node"]))
            
            page_info = data["data"]["user"]["edge_followed_by"]["page_info"]
            if not page_info["has_next_page"]:
                break
            
            after = page_info["end_cursor"]
        
        return followers
    
    async def get_all_following(self, username: str) -> List[Dict]:
        """Get all following for a username"""
        user_id = await self.get_user_id(username)
        if not user_id:
            return []
        
        following = []
        after = None
        
        while True:
            data = await self.fetch_following(user_id, after=after)
            
            if not data or "data" not in data:
                break
            
            edges = data["data"]["user"]["edge_follow"]["edges"]
            for edge in edges:
                following.append(self.parse_user_data(edge["node"]))
            
            page_info = data["data"]["user"]["edge_follow"]["page_info"]
            if not page_info["has_next_page"]:
                break
            
            after = page_info["end_cursor"]
        
        return following