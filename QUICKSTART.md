# Instagram Intelligence Dashboard - Quick Start Guide

Get up and running in 5 minutes!

## 🚀 Fastest Setup (Docker)

### 1. Prerequisites
- Windows 11 with Docker Desktop installed
- Git installed

### 2. Clone & Setup (2 minutes)

```powershell
# Clone repository
git clone https://github.com/yourusername/instagram-intelligence-dashboard.git
cd instagram-intelligence-dashboard

# Create environment file
copy .env.example .env.production
```

### 3. Configure Credentials (1 minute)

Edit `.env.production`:

```env
# Required fields only
SECRET_KEY=your-32-character-secret-key-here
ENCRYPTION_KEY=another-32-character-key-here
INSTAGRAM_USERNAME=your_instagram_email@example.com
INSTAGRAM_PASSWORD=your_instagram_password
```

### 4. Start Services (2 minutes)

```powershell
# Run the startup script
.\scripts\startup.ps1 -Mode docker
```

### 5. Access Dashboard

Open browser to: `http://localhost`

## 🎯 First Scrape

1. **Add Account**
   - Click "Add Account" button
   - Enter Instagram username (without @)
   - Click "Add"

2. **Start Scrape**
   - Click on the account card
   - Choose "Followers" or "Following"
   - Toggle "Use credentials" if account is private
   - Click "Start Scrape"

3. **Monitor Progress**
   - Watch real-time progress bar
   - See current rate limit status
   - View discovered followers count

4. **Export Data**
   - Go to account details
   - Click "Export" button
   - Choose XLSX or CSV format

## ⚡ Essential Commands

### Docker Commands

```powershell
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
.\scripts\shutdown.ps1 -Mode docker

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Check health
curl http://localhost:8000/api/health
```

### Backup & Restore

```powershell
# Manual backup
.\scripts\backup.ps1

# Restore from backup
# 1. Stop services
.\scripts\shutdown.ps1
# 2. Extract backup
Expand-Archive backups\2024-01-15_03-00-00.zip -DestinationPath restore_temp
# 3. Copy database
copy restore_temp\instagram_intel.db data\instagram_intel.db
# 4. Restart services
.\scripts\startup.ps1
```

## 🔧 Quick Configuration

### Rate Limits (in .env.production)

```env
# Conservative (Default - Recommended)
RATE_LIMIT_PER_MINUTE=2

# Moderate 
RATE_LIMIT_PER_MINUTE=3

# Aggressive (Risky)
RATE_LIMIT_PER_MINUTE=3.3
```

### Scrape Delays

```env
# Default (Safe)
SCRAPE_DELAY_SECONDS=30
JITTER_SECONDS_MIN=10
JITTER_SECONDS_MAX=20

# Faster (Less Safe)
SCRAPE_DELAY_SECONDS=20
JITTER_SECONDS_MIN=5
JITTER_SECONDS_MAX=10
```

## 🚨 Troubleshooting

### Service Won't Start

```powershell
# Check Docker is running
docker version

# Check ports aren't in use
netstat -an | findstr ":8000"
netstat -an | findstr ":3000"

# Clean restart
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### Authentication Issues

1. Verify Instagram credentials in `.env.production`
2. Check for 2FA on your Instagram account
3. Try logging into Instagram web to clear any blocks
4. Check spam folder for Instagram security emails

### Rate Limiting

If you see "Rate limit exceeded":

1. Wait 11 minutes (sliding window reset)
2. Reduce `RATE_LIMIT_PER_MINUTE` to 1
3. Increase `SCRAPE_DELAY_SECONDS` to 60
4. Restart services

### Database Issues

```powershell
# If database is locked
# 1. Stop all services
.\scripts\shutdown.ps1

# 2. Copy database
copy data\instagram_intel.db data\instagram_intel.backup.db

# 3. Delete lock file if exists
del data\instagram_intel.db-wal
del data\instagram_intel.db-shm

# 4. Restart
.\scripts\startup.ps1
```

## 📱 Remote Access via Tailscale

1. Install Tailscale on server and client
2. Join same Tailscale network
3. Update `.env.production`:
   ```env
   ALLOWED_ORIGINS=http://localhost:3000,https://your-tailscale-hostname
   ```
4. Access via: `https://your-tailscale-hostname`

## 🔐 Security Quick Tips

1. **Never commit .env files**
2. **Use strong SECRET_KEY and ENCRYPTION_KEY**
3. **Enable Windows Firewall**
4. **Use HTTPS in production**
5. **Regularly update dependencies**

## 📞 Need Help?

- Check logs: `docker-compose logs`
- Health endpoint: `http://localhost:8000/api/health`
- Full docs: See [README.md](README.md)
- Deployment guide: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

*Happy scraping! Remember to respect Instagram's terms of service.*