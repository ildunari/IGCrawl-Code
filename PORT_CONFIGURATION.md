# Instagram Intelligence Dashboard - Port Configuration

## Current Port Assignment

The application has been configured to use the following ports:

### Service Ports:
- **Frontend**: Port `8090` (changed from default 80)
- **Backend API**: Port `8000`
- **Redis**: Port `6379`

### Access URLs:
- **Frontend Dashboard**: http://localhost:8090
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/v1/health

## Configuration Files Updated:

1. `docker-compose.yml`
   - Frontend port mapping changed from `"80:80"` to `"8090:80"`

2. `docker-compose.prod.yml`
   - Nginx port mapping changed from `"80:80"` to `"8090:80"`

3. `.env` and `.env.template`
   - ALLOWED_ORIGINS includes `http://localhost:8090`

4. `backend/app/config.py`
   - Default allowed_origins includes `http://localhost:8090`

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (development)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:8090` (production frontend)

## Why Port 8090?

- Avoids conflict with other web applications on Windows servers
- Port 80 is commonly used by default web servers
- 8090 is a non-standard port unlikely to conflict
- Easy to remember and type

## Changing the Port

If you need to use a different port, update:

1. `docker-compose.yml` - Change the frontend port mapping
2. `.env` - Update ALLOWED_ORIGINS to include your new port
3. Rebuild and restart the containers:
   ```bash
   docker compose down
   docker compose build
   docker compose up -d
   ```

## Windows Firewall

Remember to open port 8090 in Windows Firewall:
```powershell
New-NetFirewallRule -DisplayName "Instagram Dashboard Frontend" -Direction Inbound -LocalPort 8090 -Protocol TCP -Action Allow
```