#!/usr/bin/env pwsh
# Start JuteVision Streamlit app and Cloudflare quick tunnel.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root
Write-Host "Starting JuteVision services..." -ForegroundColor Cyan

# Activate venv and start Streamlit
$venvPython = Join-Path $root 'venv\Scripts\python.exe'
$streamlitExe = Join-Path $root 'venv\Scripts\streamlit.exe'
if (Test-Path $streamlitExe) {
    Write-Host "Launching Streamlit..." -ForegroundColor Green
    Start-Process -FilePath $streamlitExe -ArgumentList 'run','jute_test.py','--server.port','8501','--server.headless','true' -NoNewWindow
} elseif (Test-Path $venvPython) {
    Write-Host "Launching Streamlit via python -m streamlit..." -ForegroundColor Green
    Start-Process -FilePath $venvPython -ArgumentList '-m','streamlit','run','jute_test.py','--server.port','8501','--server.headless','true' -NoNewWindow
} else {
    Write-Host "Could not find venv Python or streamlit.exe in project. Please ensure venv exists." -ForegroundColor Red
}

# Start cloudflared quick tunnel if available
$cloud = Join-Path $root 'cloudflared.exe'
if (Test-Path $cloud) {
    Write-Host "Starting Cloudflare quick tunnel..." -ForegroundColor Green
    Start-Process -FilePath $cloud -ArgumentList 'tunnel','--url','http://localhost:8501' -NoNewWindow
} else {
    Write-Host "cloudflared not found in project root. Skipping tunnel." -ForegroundColor Yellow
}

Write-Host "Services started (check processes and logs)." -ForegroundColor Cyan
