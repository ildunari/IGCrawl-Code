# PowerShell script to set up IGCrawl as a Windows service using NSSM

param(
    [string]$NSSMPath = "C:\nssm\nssm.exe",
    [string]$PythonPath = "python",
    [string]$AppPath = (Get-Location).Path,
    [string]$ServiceName = "IGCrawl"
)

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Error "This script must be run as Administrator. Exiting..."
    exit 1
}

# Check if NSSM exists
if (!(Test-Path $NSSMPath)) {
    Write-Error "NSSM not found at $NSSMPath. Please download it from https://nssm.cc/download"
    exit 1
}

# Stop service if it exists
Write-Host "Checking for existing service..."
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "Stopping existing service..."
    & $NSSMPath stop $ServiceName
    Write-Host "Removing existing service..."
    & $NSSMPath remove $ServiceName confirm
}

# Install Redis service
Write-Host "Installing Redis service..."
& $NSSMPath install "${ServiceName}_Redis" "C:\Redis\redis-server.exe"
& $NSSMPath set "${ServiceName}_Redis" AppDirectory "C:\Redis"
& $NSSMPath set "${ServiceName}_Redis" DisplayName "IGCrawl Redis Server"
& $NSSMPath set "${ServiceName}_Redis" Description "Redis server for IGCrawl Instagram Intelligence Dashboard"
& $NSSMPath set "${ServiceName}_Redis" Start SERVICE_AUTO_START

# Install Backend service
Write-Host "Installing Backend service..."
$backendPath = Join-Path $AppPath "backend"
& $NSSMPath install "${ServiceName}_Backend" $PythonPath
& $NSSMPath set "${ServiceName}_Backend" AppParameters "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
& $NSSMPath set "${ServiceName}_Backend" AppDirectory $backendPath
& $NSSMPath set "${ServiceName}_Backend" DisplayName "IGCrawl Backend API"
& $NSSMPath set "${ServiceName}_Backend" Description "FastAPI backend for IGCrawl Instagram Intelligence Dashboard"
& $NSSMPath set "${ServiceName}_Backend" Start SERVICE_AUTO_START
& $NSSMPath set "${ServiceName}_Backend" AppEnvironmentExtra "PYTHONUNBUFFERED=1"

# Install Worker service
Write-Host "Installing Worker service..."
& $NSSMPath install "${ServiceName}_Worker" $PythonPath
& $NSSMPath set "${ServiceName}_Worker" AppParameters "-m rq worker"
& $NSSMPath set "${ServiceName}_Worker" AppDirectory $backendPath
& $NSSMPath set "${ServiceName}_Worker" DisplayName "IGCrawl Worker"
& $NSSMPath set "${ServiceName}_Worker" Description "Background worker for IGCrawl Instagram Intelligence Dashboard"
& $NSSMPath set "${ServiceName}_Worker" Start SERVICE_AUTO_START
& $NSSMPath set "${ServiceName}_Worker" AppEnvironmentExtra "PYTHONUNBUFFERED=1"

# Set dependencies
& $NSSMPath set "${ServiceName}_Backend" DependOnService "${ServiceName}_Redis"
& $NSSMPath set "${ServiceName}_Worker" DependOnService "${ServiceName}_Redis"
& $NSSMPath set "${ServiceName}_Worker" DependOnService "${ServiceName}_Backend"

# Configure logging
$logPath = Join-Path $AppPath "logs"
New-Item -ItemType Directory -Force -Path $logPath

& $NSSMPath set "${ServiceName}_Redis" AppStdout (Join-Path $logPath "redis-stdout.log")
& $NSSMPath set "${ServiceName}_Redis" AppStderr (Join-Path $logPath "redis-stderr.log")
& $NSSMPath set "${ServiceName}_Backend" AppStdout (Join-Path $logPath "backend-stdout.log")
& $NSSMPath set "${ServiceName}_Backend" AppStderr (Join-Path $logPath "backend-stderr.log")
& $NSSMPath set "${ServiceName}_Worker" AppStdout (Join-Path $logPath "worker-stdout.log")
& $NSSMPath set "${ServiceName}_Worker" AppStderr (Join-Path $logPath "worker-stderr.log")

# Start services
Write-Host "Starting services..."
& $NSSMPath start "${ServiceName}_Redis"
Start-Sleep -Seconds 2
& $NSSMPath start "${ServiceName}_Backend"
Start-Sleep -Seconds 2
& $NSSMPath start "${ServiceName}_Worker"

Write-Host ""
Write-Host "Services installed successfully!"
Write-Host "You can manage them using:"
Write-Host "  nssm start ${ServiceName}_Backend"
Write-Host "  nssm stop ${ServiceName}_Backend"
Write-Host "  nssm restart ${ServiceName}_Backend"
Write-Host ""
Write-Host "The application should now be available at http://localhost:8000"

# Create a desktop shortcut
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:USERPROFILE\Desktop\IGCrawl.url")
$shortcut.TargetPath = "http://localhost:8000"
$shortcut.Save()

Write-Host "Desktop shortcut created!"