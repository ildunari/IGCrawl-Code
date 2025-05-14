# Instagram Rate Limiting Guide

## Community-Discovered Limits

Based on extensive community testing and reverse engineering:

| Endpoint | Hard Cap | Evidence |
|----------|----------|----------|
| **Public GraphQL** (`/graphql/query/`) | ~200 requests/hour per IP (3-4 req/min) | GitHub issues, Stack Overflow threads |
| **Private API** (via instagrapi) | Same 200 req/h per login session | Enforced as sliding 11-minute window |
| **Logged-out scraping** | ~100 page fetches/hr | Lower threshold, temporary shadow-bans |

Instagram's official Graph API limit for business accounts was lowered from 5,000 to 200 per hour on November 27, 2022.

## Our Implementation

### Default Configuration (Ultra-Safe)

```env
# 2 requests per minute = 120 requests per hour
# Well under the 200/hour limit
RATE_LIMIT_PER_MINUTE=2
SCRAPE_DELAY_SECONDS=30

# Random jitter to avoid patterns
JITTER_SECONDS_MIN=5
JITTER_SECONDS_MAX=15
```

**Why these defaults?**
- 2 req/min × 60 = 120 req/hour (60% of limit)
- Each call returns ~50 followers = 6,000 rows/hour
- Sufficient for most accounts overnight
- Includes random jitter to appear more human

### Sliding Window Implementation

Our rate limiter uses:
- 11-minute sliding window (Instagram's actual window)
- Per-hour tracking (200 request limit)
- Per-minute limiting (configurable)
- Automatic backoff on 429 responses

### When to Adjust Settings

| Use Case | Settings | Risk Level |
|----------|----------|------------|
| One-time export (50k followers) | `RATE_LIMIT_PER_MINUTE=3` | Medium - may hit 429 |
| With residential proxy | `RATE_LIMIT_PER_MINUTE=5` | High - monitor closely |
| Multiple concurrent jobs | Keep at 2, run sequentially | Low - recommended |

### Handling Rate Limits

When you hit a 429:
1. Automatic exponential backoff (5 min → 10 min → 20 min)
2. Request queuing with retry
3. Progress updates via SSE

### Best Practices

1. **Start Conservative**: Use default 2 req/min
2. **Monitor First 429**: Immediately reduce rate if hit
3. **Use Proxies**: Rotate IPs before credentials
4. **Sequential Jobs**: Don't run parallel scrapes
5. **Add Jitter**: Random delays prevent patterns

### Technical Details

```python
# Sliding window calculation
window_start = now - (11 * 60)  # 11 minutes
window_count = redis.zcount(key, window_start, now)

# Hour limit check
hour_count = redis.zcount(key, hour_start, now)
if hour_count >= 180:  # Stay under 200
    return False, wait_time
```

### Emergency Recovery

If completely rate limited:
1. Wait 45-60 minutes
2. Switch proxy/IP
3. Use different credentials
4. Reduce rate to 1 req/min

### Monitoring

Check rate limit status:
```bash
redis-cli
> ZRANGE rate_limit:user:username 0 -1 WITHSCORES
```

View current backoff:
```bash
> GET backoff:user:username
```

## References

- [InstaTrack GitHub Issue #5](https://github.com/Snbig/InstaTrack/issues/5)
- [Instagram API Rate Limits Analysis](https://videotap.com/blog/instagram-api-rate-limits-impact-on-video-scheduling)
- [Instaloader Rate Limit Discussion](https://github.com/instaloader/instaloader/issues/1285)