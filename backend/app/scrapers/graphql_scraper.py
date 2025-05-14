import httpx
from typing import Dict, List, Optional
import json
import re
from ..utils.crypto import decrypt_credential


class GraphQLScraper:
    """Instagram GraphQL scraper for public accounts"""
    
    BASE_URL = "https://www.instagram.com/graphql/query/"
    FOLLOWERS_HASH = "5aefa9893005572d237da5068082d8d5"  # Instagram's query hash for followers
    FOLLOWING_HASH = "6df9f20c4ad9b22fb7b35b816f0c426e"  # Instagram's query hash for following
    
    def __init__(self):
        self.session = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username"""
        try:
            response = await self.session.get(f"https://www.instagram.com/{username}/")
            if response.status_code != 200:
                return None
            
            # Extract user ID from page content
            content = response.text
            user_id_match = re.search(r'"profilePage_([0-9]+)"', content)
            if user_id_match:
                return user_id_match.group(1)
            
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
            response = await self.session.get(self.BASE_URL, params=params)
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
            response = await self.session.get(self.BASE_URL, params=params)
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
        user_id = await self.get_user_id(username)
        if not user_id:
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