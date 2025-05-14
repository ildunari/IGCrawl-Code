import pytest
import time
from app.utils.rate_limiter import SlidingWindowRateLimiter
import redis
from unittest.mock import Mock, patch


@pytest.fixture
def mock_redis():
    """Mock Redis connection"""
    mock = Mock(spec=redis.Redis)
    return mock


@pytest.fixture
def rate_limiter(mock_redis):
    """Create rate limiter with mocked Redis"""
    with patch('app.utils.rate_limiter.redis.from_url', return_value=mock_redis):
        return SlidingWindowRateLimiter()


def test_can_make_request_under_limit(rate_limiter, mock_redis):
    """Test that requests are allowed under the limit"""
    mock_redis.zcount.return_value = 0
    mock_redis.get.return_value = None
    
    can_request, wait_time = rate_limiter.can_make_request("test_user")
    
    assert can_request is True
    assert wait_time is None


def test_cannot_make_request_over_limit(rate_limiter, mock_redis):
    """Test that requests are blocked over the limit"""
    mock_redis.zcount.side_effect = [21, 180, 2]  # Over window limit
    mock_redis.get.return_value = None
    mock_redis.zrange.return_value = [(b'123456', time.time() - 300)]
    
    can_request, wait_time = rate_limiter.can_make_request("test_user")
    
    assert can_request is False
    assert wait_time > 0


def test_backoff_on_rate_limit(rate_limiter, mock_redis):
    """Test exponential backoff on rate limit hits"""
    mock_redis.get.return_value = None
    
    # First rate limit hit
    wait_time = rate_limiter.record_rate_limit_hit("test_user")
    assert wait_time == 300  # 5 minutes
    
    # Mock existing backoff
    mock_redis.get.return_value = "600"
    
    # Second rate limit hit
    wait_time = rate_limiter.record_rate_limit_hit("test_user")
    assert wait_time == 1200  # Doubled to 20 minutes


def test_jitter_calculation(rate_limiter):
    """Test that jitter is within expected range"""
    delays = [rate_limiter.get_delay_with_jitter() for _ in range(100)]
    
    # Check all delays are within expected range (30 + 5-15 seconds)
    assert all(35 <= delay <= 45 for delay in delays)
    
    # Check we get variation (not all the same)
    assert len(set(delays)) > 1