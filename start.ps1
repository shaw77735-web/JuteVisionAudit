# JuteVision - Start Backend and Frontend
# Run from project root

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

# Start backend in background
Write-Host "Starting JuteVision Backend..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    & .\venv\Scripts\Activate.ps1
    Set-Location backend
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
}

Start-Sleep -Seconds 3

# Check if Node/npm available
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Starting JuteVision Frontend..." -ForegroundColor Cyan
    Set-Location frontend
    npm run dev
} else {
    Write-Host "Backend running at http://localhost:8000" -ForegroundColor Green
    Write-Host "Frontend: npm not found. Install Node.js, then run: cd frontend && npm install && npm run dev" -ForegroundColor Yellow
    Receive-Job -Job $backendJob -Wait
}
