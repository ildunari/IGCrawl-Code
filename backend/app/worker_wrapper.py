"""
Worker wrapper to handle async tasks in RQ.
RQ doesn't natively support async functions, so we need this wrapper.
"""
import asyncio
from app.workers.tasks import scrape_instagram_account as async_scrape


def scrape_instagram_account(scrape_id: int, username: str, scrape_type: str, use_private: bool = False):
    """Sync wrapper for async scrape task"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_scrape(scrape_id, username, scrape_type, use_private))