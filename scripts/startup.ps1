# Instagram Intelligence Dashboard - Windows Startup Script
# Run with Administrator privileges

param(
    [string]$Mode = "docker",  # "docker" or "native"
    [string]$Environment = "production"
)

$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

Write-Host "Instagram Intelligence Dashboard Startup Script" -ForegroundColor Green
Write-Host "Mode: $Mode | Environment: $Environment" -ForegroundColor Yellow

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Cyan

# Check for Python (native mode)
if ($Mode -eq "native") {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Python not found. Please install Python 3.11+" -ForegroundColor Red
        exit 1
    }
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
}

# Check for Docker (docker mode)
if ($Mode -eq "docker") {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Docker not found. Please install Docker Desktop" -ForegroundColor Red
        exit 1
    }
    Write-Host "Docker: $dockerVersion" -ForegroundColor Green
}

# Create required directories
Write-Host "`nCreating directories..." -ForegroundColor Cyan
$directories = @("data", "logs", "backups", "ssl")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    }
}

# Check for environment file
$envFile = ".env.$Environment"
if (!(Test-Path $envFile)) {
    Write-Host "`nError: Environment file '$envFile' not found" -ForegroundColor Red
    Write-Host "Please create '$envFile' from '.env.example'" -ForegroundColor Yellow
    exit 1
}

# Docker mode startup
if ($Mode -eq "docker") {
    Write-Host "`nStarting Docker containers..." -ForegroundColor Cyan
    
    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down
    
    # Build images
    Write-Host "Building Docker images..." -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml build
    
    # Start containers
    Write-Host "Starting containers..." -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    Write-Host "`nWaiting for services to be ready..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    # Check health
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -ErrorAction SilentlyContinue
    if ($health) {
        Write-Host "Backend API: Healthy" -ForegroundColor Green
    } else {
        Write-Host "Backend API: Not responding" -ForegroundColor Red
    }
    
    Write-Host "`nServices started successfully!" -ForegroundColor Green
    Write-Host "Access the dashboard at: http://localhost" -ForegroundColor Yellow
}

# Native mode startup
if ($Mode -eq "native") {
    Write-Host "`nStarting native services..." -ForegroundColor Cyan
    
    # Check Redis
    $redisRunning = Get-Service -Name Redis -ErrorAction SilentlyContinue
    if (!$redisRunning) {
        Write-Host "Starting Redis via WSL..." -ForegroundColor Yellow
        wsl sudo service redis-server start
    }
    
    # Install Python dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    Set-Location backend
    pip install -r requirements.txt
    
    # Install frontend dependencies and build
    Write-Host "Building frontend..." -ForegroundColor Yellow
    Set-Location ../frontend
    npm install
    npm run build
    
    # Start backend API
    Write-Host "Starting backend API..." -ForegroundColor Yellow
    Set-Location ../backend
    $apiProcess = Start-Process -FilePath "python" -ArgumentList "run_production.py" -PassThru -WindowStyle Hidden
    
    # Start worker
    Write-Host "Starting worker..." -ForegroundColor Yellow
    $workerProcess = Start-Process -FilePath "python" -ArgumentList "-m", "rq", "worker", "--url", "redis://localhost:6379" -PassThru -WindowStyle Hidden
    
    # Start nginx (if available)
    $nginxPath = "C:\nginx\nginx.exe"
    if (Test-Path $nginxPath) {
        Write-Host "Starting nginx..." -ForegroundColor Yellow
        Start-Process -FilePath $nginxPath -WorkingDirectory "C:\nginx" -WindowStyle Hidden
    }
    
    Write-Host "`nServices started successfully!" -ForegroundColor Green
    Write-Host "Backend PID: $($apiProcess.Id)" -ForegroundColor Yellow
    Write-Host "Worker PID: $($workerProcess.Id)" -ForegroundColor Yellow
    Write-Host "Access the dashboard at: http://localhost:3000" -ForegroundColor Yellow
    
    # Save PIDs for shutdown script
    @{
        API = $apiProcess.Id
        Worker = $workerProcess.Id
    } | ConvertTo-Json | Out-File -FilePath "pids.json"
}

# Setup scheduled tasks
Write-Host "`nSetting up scheduled tasks..." -ForegroundColor Cyan

# Backup task
$backupAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ProjectRoot\scripts\backup.ps1`""
$backupTrigger = New-ScheduledTaskTrigger -Daily -At 3:00AM
$backupPrincipal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest

try {
    Register-ScheduledTask -TaskName "IGCrawl Daily Backup" -Action $backupAction -Trigger $backupTrigger -Principal $backupPrincipal -Force
    Write-Host "Scheduled daily backup at 3:00 AM" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not create backup task" -ForegroundColor Yellow
}

# Log rotation task
$logAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ProjectRoot\scripts\rotate_logs.ps1`""
$logTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2:00AM

try {
    Register-ScheduledTask -TaskName "IGCrawl Log Rotation" -Action $logAction -Trigger $logTrigger -Principal $backupPrincipal -Force
    Write-Host "Scheduled weekly log rotation on Sundays at 2:00 AM" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not create log rotation task" -ForegroundColor Yellow
}

# Display status
Write-Host "`n=== Startup Complete ===" -ForegroundColor Green
Write-Host "Dashboard URL: http://localhost" -ForegroundColor Cyan
Write-Host "API URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/api/health" -ForegroundColor Cyan

if ($Mode -eq "docker") {
    Write-Host "`nDocker commands:" -ForegroundColor Yellow
    Write-Host "  View logs: docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Gray
    Write-Host "  Stop services: docker-compose -f docker-compose.prod.yml down" -ForegroundColor Gray
    Write-Host "  Restart services: docker-compose -f docker-compose.prod.yml restart" -ForegroundColor Gray
}

if ($Mode -eq "native") {
    Write-Host "`nService PIDs saved to pids.json" -ForegroundColor Yellow
    Write-Host "Use shutdown.ps1 to stop services" -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")