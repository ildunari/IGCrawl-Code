# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a self-hosted Instagram intelligence dashboard that scrapes follower/following data from Instagram accounts and provides a comprehensive UI for viewing, analyzing, and exporting this data.

## Technical Architecture

### Backend (Python)
- **Framework**: FastAPI
- **Database**: SQLite with SQLModel ORM
- **Background Jobs**: RQ (Redis Queue) 
- **Instagram API**: GraphQL + instagrapi fallback strategy
- **Caching**: Redis for API response caching (24h TTL)

### Frontend (React)
- **Framework**: React 18 with Vite
- **Styling**: TailwindCSS + shadcn/ui components
- **Charts**: Recharts for data visualization
- **Optional**: sigma.js for network visualization

### Deployment
- Docker Compose for containerized deployment
- Windows 11 service using NSSM
- Accessible via Tailscale network

## Key Database Schema

Three main tables:
- `accounts`: Target Instagram accounts being tracked
- `scrapes`: Individual scrape runs with metadata
- `followers`: Follower/following data with composite PK (target_id, follower_id)

## Important API Endpoints

- `/api/scrape`: Enqueues new scrape job
- `/api/progress/{job_id}`: Server-sent events for scrape progress
- `/api/accounts`: CRUD operations for target accounts
- `/api/export`: Generate CSV/XLSX/JSON exports

## Development Commands

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Redis (required for background jobs)
```bash
redis-server
```

### Worker Process
```bash
cd backend
rq worker
```

### Run Tests
```bash
cd backend
pytest
```

### Build for Production
```bash
cd frontend
npm run build
```

### Docker Deployment
```bash
docker-compose up -d
```

## Security & Credentials

- Instagram credentials are AES-256 encrypted in .env
- Master key stored in Windows Credential Manager
- Optional passphrase unlock modal for remote access
- CSRF & CORS restricted to Tailscale network

## Data Collection

When scraping Instagram accounts, capture these fields:
- `profile_pic_url`: For thumbnail grid display
- `is_verified`: For UI badge display
- `full_name`: For searchable column
- Standard follower/following relationship data

## UI Components

Key pages to implement:
1. **Dashboard**: KPIs, charts, global search
2. **Accounts**: DataTable with CRUD actions
3. **Followers View**: Tabbed interface (Followers/Following/Mutuals)
4. **Scrape Modal**: Input validation, progress tracking
5. **Settings**: Credential management, proxy config, rate limits

## Testing Guidelines

- Test API endpoints with pytest
- Mock Instagram API responses for unit tests
- Test Redis queue functionality
- Frontend component testing with React Testing Library

## Performance Considerations

- Implement pagination for large datasets
- Use Redis caching to reduce API calls
- Background jobs for long-running scrapes
- Infinite scroll for data tables