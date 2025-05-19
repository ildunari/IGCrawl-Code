# Instagram Intelligence Dashboard - Production Deployment Guide

This guide covers the complete deployment process for the Instagram Intelligence Dashboard on Windows 11 with Tailscale access.

## Prerequisites

- Windows 11 (22H2 or later)
- Python 3.11+
- Node.js 18+
- Redis (via Windows Subsystem for Linux or Docker)
- Docker Desktop (optional but recommended)
- Tailscale account

## 1. Production Setup on Windows 11

### Option A: Docker Deployment (Recommended)

1. Install Docker Desktop for Windows
2. Clone the repository:
   ```powershell
   git clone https://github.com/yourusername/instagram-intelligence-dashboard.git
   cd instagram-intelligence-dashboard
   ```

3. Create production environment file:
   ```powershell
   copy .env.example .env.production
   ```

4. Update `.env.production` with production values (see Environment Variables section)

5. Build and run with Docker Compose:
   ```powershell
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Option B: Native Windows Service

1. Install Redis via WSL:
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo service redis-server start
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   cd frontend
   npm install
   npm run build
   ```

3. Install NSSM (Non-Sucking Service Manager):
   ```powershell
   choco install nssm
   ```

4. Create Windows services:
   ```powershell
   # Backend API service
   nssm install IGCrawlAPI "C:\Python311\python.exe" "C:\path\to\project\backend\run_production.py"
   nssm set IGCrawlAPI AppDirectory "C:\path\to\project\backend"
   nssm set IGCrawlAPI AppEnvironmentExtra "PYTHONPATH=C:\path\to\project\backend"
   
   # Worker service
   nssm install IGCrawlWorker "C:\Python311\python.exe" "-m" "rq" "worker" "--url" "redis://localhost:6379"
   nssm set IGCrawlWorker AppDirectory "C:\path\to\project\backend"
   
   # Start services
   nssm start IGCrawlAPI
   nssm start IGCrawlWorker
   ```

## 2. Environment Variable Configuration

Create `.env.production` with the following:

```env
# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENCRYPTION_KEY=<generate-with-openssl-rand-hex-32>

# Database
DATABASE_URL=sqlite:///./data/instagram_intel.db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,https://your-tailscale-hostname

# Instagram Configuration
INSTAGRAM_USERNAME=your_account@email.com
INSTAGRAM_PASSWORD=your_password

# Rate Limiting (Production Safe Defaults)
RATE_LIMIT_PER_MINUTE=2
SCRAPE_DELAY_SECONDS=30
JITTER_SECONDS_MIN=10
JITTER_SECONDS_MAX=20

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=30
BACKUP_DIRECTORY=/data/backups

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
LOG_LEVEL=INFO
```

## 3. Setting Up Instagram Credentials Securely

1. Create encrypted credentials file:
   ```python
   # run_encrypt_credentials.py
   from app.utils.encryption import encrypt_password
   
   username = input("Instagram username: ")
   password = input("Instagram password: ")
   
   encrypted = encrypt_password(password)
   
   with open('data/credentials.enc', 'w') as f:
       f.write(f"{username}|{encrypted}")
   ```

2. Run the script:
   ```powershell
   python run_encrypt_credentials.py
   ```

3. Set file permissions:
   ```powershell
   icacls "data\credentials.enc" /inheritance:r /grant:r "%USERNAME%:(R)"
   ```

## 4. Configuring Tailscale Access

1. Install Tailscale:
   ```powershell
   winget install tailscale
   ```

2. Configure Tailscale:
   ```powershell
   tailscale up --advertise-routes=192.168.1.0/24
   ```

3. Update nginx configuration (if using):
   ```nginx
   server {
       listen 80;
       server_name your-tailscale-hostname;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header Host $host;
       }
   }
   ```

## 5. Setting Up Auto-Archived Backups

1. Create backup script (`scripts/backup.ps1`):
   ```powershell
   $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
   $backupDir = "C:\path\to\project\data\backups\$timestamp"
   
   # Create backup directory
   New-Item -ItemType Directory -Path $backupDir
   
   # Backup database
   Copy-Item "C:\path\to\project\data\instagram_intel.db" "$backupDir\instagram_intel.db"
   
   # Backup logs
   Copy-Item "C:\path\to\project\logs\*" "$backupDir\logs\" -Recurse
   
   # Create archive
   Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"
   Remove-Item $backupDir -Recurse
   
   # Clean old backups (older than 30 days)
   Get-ChildItem "C:\path\to\project\data\backups\*.zip" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
   ```

2. Schedule backup task:
   ```powershell
   $trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM
   $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\path\to\project\scripts\backup.ps1"
   Register-ScheduledTask -TaskName "IGCrawl Backup" -Trigger $trigger -Action $action -RunLevel Highest
   ```

## 6. Monitoring and Maintenance

### Health Check Endpoint

The application provides a health check endpoint at `/api/health`:

```powershell
# Check health
Invoke-RestMethod -Uri "http://localhost:8000/api/health"
```

### Monitoring with Prometheus (Optional)

1. Add Prometheus metrics endpoint:
   ```python
   from prometheus_client import Counter, Histogram, generate_latest
   
   scrape_counter = Counter('instagram_scrapes_total', 'Total number of scrapes')
   scrape_duration = Histogram('instagram_scrape_duration_seconds', 'Scrape duration')
   
   @app.get("/metrics")
   def metrics():
       return Response(generate_latest(), media_type="text/plain")
   ```

2. Configure Prometheus scraping:
   ```yaml
   scrape_configs:
     - job_name: 'igcrawl'
       static_configs:
         - targets: ['localhost:8000']
   ```

### Log Management

1. Configure Windows Event Log:
   ```powershell
   New-EventLog -LogName Application -Source "IGCrawl"
   ```

2. Set up log rotation:
   ```powershell
   # Add to scripts/rotate_logs.ps1
   $logDir = "C:\path\to\project\logs"
   $maxAge = 7
   
   Get-ChildItem $logDir -Filter "*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-$maxAge)} | Remove-Item
   ```

### Performance Optimization

1. Enable production mode:
   ```env
   NODE_ENV=production
   REACT_APP_API_URL=https://your-tailscale-hostname/api
   ```

2. Enable caching headers:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   from fastapi.middleware.gzip import GZipMiddleware
   
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

3. Configure static file serving:
   ```python
   from fastapi.staticfiles import StaticFiles
   
   app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
   ```

## 7. Security Best Practices

1. Enable Windows Firewall rules:
   ```powershell
   New-NetFirewallRule -DisplayName "IGCrawl API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Private
   ```

2. Set up SSL/TLS with Let's Encrypt (via Tailscale):
   ```bash
   tailscale cert your-tailscale-hostname
   ```

3. Enable rate limiting and request validation:
   ```python
   from fastapi_limiter import FastAPILimiter
   from fastapi_limiter.depends import RateLimiter
   
   @app.post("/api/v1/accounts", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
   async def create_account(...):
       ...
   ```

## 8. Database Optimization

1. Enable SQLite optimizations:
   ```python
   from sqlalchemy import event
   
   @event.listens_for(engine, "connect")
   def set_sqlite_pragma(dbapi_connection, connection_record):
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA journal_mode=WAL")
       cursor.execute("PRAGMA synchronous=NORMAL")
       cursor.execute("PRAGMA temp_store=MEMORY")
       cursor.close()
   ```

2. Create indexes for common queries:
   ```sql
   CREATE INDEX idx_followers_account_id ON followers(account_id);
   CREATE INDEX idx_followers_created_at ON followers(created_at);
   CREATE INDEX idx_scrapes_status ON scrapes(status);
   ```

## 9. Troubleshooting

### Common Issues

1. **Rate limiting errors**:
   - Check current rate limits in `/api/v1/system/rate-limits`
   - Adjust RATE_LIMIT_PER_MINUTE in environment

2. **Authentication failures**:
   - Verify Instagram credentials are correct
   - Check for 2FA requirements
   - Review Instagram security emails

3. **Worker not processing jobs**:
   - Verify Redis is running: `redis-cli ping`
   - Check worker logs: `nssm stdout IGCrawlWorker`
   - Restart worker service: `nssm restart IGCrawlWorker`

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
FASTAPI_DEBUG=true
```

## 10. Backup Recovery

To restore from backup:

1. Stop all services:
   ```powershell
   nssm stop IGCrawlAPI
   nssm stop IGCrawlWorker
   ```

2. Extract backup:
   ```powershell
   Expand-Archive -Path "backups\2024-01-15_03-00-00.zip" -DestinationPath "restore_temp"
   ```

3. Restore database:
   ```powershell
   Copy-Item "restore_temp\instagram_intel.db" "data\instagram_intel.db" -Force
   ```

4. Restart services:
   ```powershell
   nssm start IGCrawlAPI
   nssm start IGCrawlWorker
   ```

## Maintenance Schedule

- **Daily**: Automated backups at 3 AM
- **Weekly**: Log rotation and cleanup
- **Monthly**: Database optimization and index rebuilding
- **Quarterly**: Security updates and dependency upgrades

## Support

For issues or questions:
1. Check application logs in `/logs` directory
2. Review health check endpoint: `http://localhost:8000/api/health`
3. Monitor Redis queue: `redis-cli llen rq:queue:default`
4. Check system metrics in Task Manager or Performance Monitor

---

*Last updated: January 2024*