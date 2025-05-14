# Instagram Intelligence Dashboard - Windows Shutdown Script

param(
    [string]$Mode = "docker"  # "docker" or "native"
)

$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

Write-Host "Instagram Intelligence Dashboard Shutdown Script" -ForegroundColor Red
Write-Host "Mode: $Mode" -ForegroundColor Yellow

# Docker mode shutdown
if ($Mode -eq "docker") {
    Write-Host "`nStopping Docker containers..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker containers stopped successfully" -ForegroundColor Green
    } else {
        Write-Host "Error stopping Docker containers" -ForegroundColor Red
    }
}

# Native mode shutdown
if ($Mode -eq "native") {
    Write-Host "`nStopping native services..." -ForegroundColor Cyan
    
    # Read PIDs from file
    if (Test-Path "pids.json") {
        $pids = Get-Content "pids.json" | ConvertFrom-Json
        
        # Stop API
        if ($pids.API) {
            Write-Host "Stopping API (PID: $($pids.API))..." -ForegroundColor Yellow
            Stop-Process -Id $pids.API -Force -ErrorAction SilentlyContinue
        }
        
        # Stop Worker
        if ($pids.Worker) {
            Write-Host "Stopping Worker (PID: $($pids.Worker))..." -ForegroundColor Yellow
            Stop-Process -Id $pids.Worker -Force -ErrorAction SilentlyContinue
        }
        
        # Remove PID file
        Remove-Item "pids.json" -Force
    } else {
        Write-Host "No PID file found. Looking for processes by name..." -ForegroundColor Yellow
        
        # Try to find and stop processes by name
        Get-Process python | Where-Object {
            $_.CommandLine -like "*run_production.py*" -or
            $_.CommandLine -like "*rq worker*"
        } | ForEach-Object {
            Write-Host "Stopping process: $($_.Id)" -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force
        }
    }
    
    # Stop nginx if running
    Get-Process nginx -ErrorAction SilentlyContinue | Stop-Process -Force
    
    # Optionally stop Redis in WSL
    $stopRedis = Read-Host "`nStop Redis in WSL? (y/n)"
    if ($stopRedis -eq 'y') {
        wsl sudo service redis-server stop
        Write-Host "Redis stopped" -ForegroundColor Green
    }
}

Write-Host "`nShutdown complete" -ForegroundColor Green