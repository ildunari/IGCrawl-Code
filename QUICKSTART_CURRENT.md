# IGCrawl Quick Start Guide - Current State

This guide reflects the current working state of IGCrawl as of May 14, 2025.

## Prerequisites

- Docker Desktop installed and running
- Basic terminal/command line knowledge

## Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IGCrawl-Code
   ```

2. **Create environment file**
   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Edit the .env file**
   ```env
   # Set proxy to false due to authentication issues
   USE_PROXY=false
   
   # Optional: Add your Instagram credentials
   INSTAGRAM_USERNAME=your_username
   INSTAGRAM_PASSWORD=your_password
   ```

4. **Start the application**
   ```bash
   docker compose up -d
   ```

5. **Access the application**
   - Frontend: http://localhost:8090
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Testing the Application

1. **Navigate to Accounts page**
   - Click "Accounts" in the sidebar
   - If no accounts show, try refreshing the page (Cmd+Shift+R)

2. **Add a test account**
   - Click "Add Account"
   - Enter username: "vitamintk" (or any public Instagram account)
   - Click "Add Account"

3. **Run a scrape**
   - Click "Run scrape" button next to the account
   - You'll be redirected to the scrape progress page
   - The scrape will complete but may return 0 followers due to proxy issues

4. **Check scrape results**
   - Navigate to "Scrapes" page
   - You may need to refresh if no results show
   - Alternatively, check the API directly: http://localhost:8000/api/v1/scrapes/account/1?limit=10

## Known Limitations

1. **Proxy Issues**: BrightData proxy authentication fails, disable with `USE_PROXY=false`
2. **Zero Followers**: Scrapes complete but return 0 followers without working proxy
3. **Frontend Updates**: Pages may require hard refresh to show updated data
4. **Rate Limiting**: Instagram may rate limit requests without proxy protection

## Monitoring

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
# Backend logs
docker compose logs backend -f

# Worker logs
docker compose logs worker -f

# All services
docker compose logs -f
```

### Clear Rate Limits (if needed)
```bash
docker compose exec redis redis-cli FLUSHALL
```

## Troubleshooting

1. **Services not starting**
   ```bash
   docker compose down
   docker compose up -d
   ```

2. **Database locked errors**
   ```bash
   docker compose restart backend worker
   ```

3. **Frontend not updating**
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
   - Clear browser cache

4. **Worker not processing jobs**
   ```bash
   docker compose restart worker
   docker compose logs worker -f
   ```

## API Testing

Test the API directly:

```bash
# Check account list
curl http://localhost:8000/api/v1/accounts/

# Get specific account
curl http://localhost:8000/api/v1/accounts/1

# Check scrape status
curl http://localhost:8000/api/v1/scrapes/account/1?limit=10
```

## Next Steps

For production deployment or to fix proxy issues, see:
- [README.md](README.md) for full documentation
- [PROJECT_STATUS_2025_05_14.md](PROJECT_STATUS_2025_05_14.md) for current issues
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production setup

## Important Notes

- The application is functional but limited by proxy authentication issues
- Consider using without proxy for testing purposes only
- Instagram may rate limit or block requests without proper proxy
- Always respect Instagram's Terms of Service