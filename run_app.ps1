# JuteVision - Run full app (backend + serve frontend for phone/desktop)
# From project root. Build frontend first so backend can serve it.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

# Build frontend if Node available
$nodePath = "C:\Program Files\nodejs"
if (Test-Path "$nodePath\npm.cmd") {
    $env:Path = "$nodePath;$env:Path"
    Write-Host "Building frontend..." -ForegroundColor Cyan
    Set-Location frontend
    npm run build 2>&1 | Out-Null
    Set-Location $root
}

# Start backend (serves API + video feed + frontend when frontend/dist exists)
Write-Host "Starting JuteVision backend..." -ForegroundColor Cyan
Write-Host "  Desktop: http://localhost:8000" -ForegroundColor Green
Write-Host "  Phone:   http://<THIS_PC_IP>:8000  (same Wi-Fi)" -ForegroundColor Green
Write-Host ""
& .\venv\Scripts\Activate.ps1
Set-Location backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
