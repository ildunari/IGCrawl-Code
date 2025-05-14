# Instagram Intelligence Dashboard v2

A self-hosted Instagram analytics tool that safely crawls follower/following data for any handle (public or private) and provides powerful browsing, filtering, charting, and export capabilities.

## 🚀 Quick Start

### Docker Deployment (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/instagram-intelligence-dashboard.git
   cd instagram-intelligence-dashboard
   ```

2. Copy and configure environment file:
   ```bash
   cp .env.example .env.production
   # Edit .env.production with your settings
   ```

3. Run the startup script:
   ```powershell
   .\scripts\startup.ps1 -Mode docker -Environment production
   ```

4. Access the dashboard at `http://localhost:8090`

### Native Windows Deployment

1. Install prerequisites:
   - Python 3.11+
   - Node.js 18+
   - Redis (via WSL)

2. Run the startup script:
   ```powershell
   .\scripts\startup.ps1 -Mode native -Environment production
   ```

## 🎯 Features

- **Smart Instagram Scraping**: Safely scrapes followers/following data with built-in rate limiting
- **Support for Private Accounts**: Login support for accessing private profiles
- **Intelligent Rate Limiting**: Sliding window algorithm stays well under Instagram's 200 req/hour limit
- **Real-time Progress Tracking**: SSE-powered live updates during scraping
- **Advanced Filtering**: Filter by verified status, follower count, mutual connections
- **Data Visualization**: Interactive charts for follower growth and demographics
- **Export Capabilities**: One-click XLSX/CSV downloads with custom templates
- **Dark Mode UI**: Touch-friendly interface optimized for all devices
- **Automated Backups**: Daily archived snapshots with 30-day retention
- **Windows Service**: Runs as a background service with Tailscale access

## 🛡️ Security & Rate Limiting

The application implements Instagram's actual rate limits based on community research:

- **Safe Default**: 2 requests/minute (120/hour)
- **Hard Cap**: 200 requests/hour (Instagram's limit)
- **Sliding Window**: 11-minute tracking window
- **Smart Delays**: 30-60 second intervals with random jitter
- **Exponential Backoff**: Automatic retry with increasing delays

## 📊 Technology Stack

### Backend
- **FastAPI**: High-performance async API framework
- **SQLModel**: Type-safe ORM with SQLite
- **Redis + RQ**: Background job processing
- **instagrapi**: Instagram private API client
- **Sliding Window Rate Limiter**: Custom implementation

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Lightning-fast build tool
- **TailwindCSS**: Utility-first styling
- **shadcn/ui**: Accessible component library
- **Recharts**: Data visualization

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   ├── utils/        # Utilities (encryption, rate limiting)
│   │   └── workers/      # Background job handlers
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   └── lib/          # Utilities and API client
│   └── package.json
├── scripts/
│   ├── startup.ps1       # Windows startup script
│   ├── shutdown.ps1      # Graceful shutdown
│   └── backup.ps1        # Automated backup
├── docker-compose.yml    # Development setup
├── docker-compose.prod.yml # Production setup
└── nginx.conf           # Production web server config
```

## 🔧 Configuration

### Environment Variables

```env
# Security
SECRET_KEY=<32-byte-hex>
ENCRYPTION_KEY=<32-byte-hex>

# Instagram
INSTAGRAM_USERNAME=your_email@example.com
INSTAGRAM_PASSWORD=your_password

# Rate Limiting
RATE_LIMIT_PER_MINUTE=2
SCRAPE_DELAY_SECONDS=30

# Database
DATABASE_URL=sqlite:///./data/instagram_intel.db

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Rate Limiting Configuration

Adjust rate limits based on your needs:

```python
# Conservative (Recommended)
RATE_LIMIT_PER_MINUTE=2  # 120/hour

# Moderate
RATE_LIMIT_PER_MINUTE=3  # 180/hour

# Aggressive (Use with caution)
RATE_LIMIT_PER_MINUTE=3.3  # 198/hour
```

## 📈 API Endpoints

### Accounts
- `GET /api/v1/accounts` - List all accounts
- `POST /api/v1/accounts` - Add new account
- `GET /api/v1/accounts/{id}` - Get account details

### Scrapes
- `POST /api/v1/accounts/{id}/scrape` - Start new scrape
- `GET /api/v1/scrapes/{id}` - Get scrape status
- `GET /api/v1/scrapes/{id}/progress` - Real-time progress (SSE)

### Data Operations
- `GET /api/v1/accounts/{id}/followers` - Get followers with filtering
- `GET /api/v1/accounts/{id}/charts` - Get chart data
- `POST /api/v1/accounts/{id}/export` - Export to XLSX/CSV

### System
- `GET /api/health` - Health check
- `GET /api/v1/system/rate-limits` - Current rate limit status

## 🚦 Monitoring

### Health Checks
```bash
curl http://localhost:8000/api/health
```

### Rate Limit Status
```bash
curl http://localhost:8000/api/v1/system/rate-limits
```

### Docker Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔒 Security Best Practices

1. **Credential Encryption**: All Instagram credentials are AES-256 encrypted
2. **Environment Isolation**: Sensitive data stored in `.env` files
3. **Network Security**: Use Tailscale for secure remote access
4. **Rate Limiting**: Prevents Instagram account flagging
5. **Input Validation**: All API inputs are validated
6. **HTTPS Only**: Production deployment uses SSL/TLS

## 🛠️ Maintenance

### Daily Tasks (Automated)
- Database backup at 3 AM
- Log rotation and cleanup

### Weekly Tasks
- Review rate limit metrics
- Check Instagram authentication status
- Monitor disk usage

### Monthly Tasks
- Update dependencies
- Optimize database indexes
- Review security logs

## 🐛 Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**
   - Reduce `RATE_LIMIT_PER_MINUTE`
   - Increase `SCRAPE_DELAY_SECONDS`
   - Check recent request history

2. **Authentication Failed**
   - Verify Instagram credentials
   - Check for 2FA requirements
   - Review Instagram security emails

3. **Worker Not Processing**
   - Check Redis connectivity
   - Verify worker service status
   - Review worker logs

4. **Database Locked**
   - Enable WAL mode (automatic)
   - Check for long-running queries
   - Restart services if needed

## 📦 Deployment Guide

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed production deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with Instagram's Terms of Service and applicable laws. The developers are not responsible for any misuse or violations.

---

Built with ❤️ for the data analytics community