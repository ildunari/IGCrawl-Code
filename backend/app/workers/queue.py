import redis
from rq import Queue
from ..config import get_settings

settings = get_settings()

# Redis connection
redis_conn = redis.from_url(settings.redis_url)

# RQ queue
queue = Queue(connection=redis_conn, default_timeout=settings.worker_timeout)