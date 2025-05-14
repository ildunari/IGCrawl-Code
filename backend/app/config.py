from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "Instagram Intelligence Dashboard"
    debug: bool = False
    
    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Security
    secret_key: str = "change-me-in-production"
    encryption_key: str = "change-me-in-production"
    
    # Database
    database_url: str = "sqlite:///./instagram_intel.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Instagram Configuration
    instagram_username: Optional[str] = None
    instagram_password: Optional[str] = None
    use_instagram_cache: bool = True
    instagram_cache_ttl: int = 3600  # 1 hour
    
    # Rate Limiting (based on Instagram's actual limits)
    rate_limit_per_minute: int = 2  # Safe: 120 req/h (well under 200/h cap)
    scrape_delay_seconds: int = 30  # 30 seconds between requests
    jitter_seconds_min: int = 5  # Minimum random jitter
    jitter_seconds_max: int = 15  # Maximum random jitter
    
    # Scraping Configuration
    max_retries: int = 3
    timeout_seconds: int = 30
    max_followers_per_scrape: int = 10000
    batch_size: int = 100
    
    # Export Configuration
    export_batch_size: int = 5000
    export_timeout_seconds: int = 300
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

def get_settings():
    return settings