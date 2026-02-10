# JuteVision 4G Live Access Setup
# This script creates public tunnels so you can access from 4G phone

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║          JuteVision - 4G Live Access Tunnel                   ║
║  Access your app from 4G phone + Same Wi-Fi simultaneously    ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

# Kill any existing processes
taskkill /F /FI "IMAGENAME eq streamlit.exe" 2>$null
Start-Sleep -Seconds 2

# Check if ngrok is installed
$ngrokPath = "C:\tools\ngrok\ngrok.exe"
if (-not (Test-Path $ngrokPath)) {
    $ngrokPath = "ngrok"
}

Write-Host "
📍 STEP 1: LOCAL ACCESS (Same Wi-Fi)" -ForegroundColor Cyan
Write-Host "Starting Streamlit on port 8500..."

# Start Streamlit
cd "c:\Users\AFTAB\Desktop\New folder\JuteVision"
.\venv\Scripts\streamlit.exe run jute_test.py --server.port=8500 --server.address="0.0.0.0" --server.enableCORS=false &
$streamlitPID = $PID

Start-Sleep -Seconds 6

Write-Host "✅ Streamlit is running!" -ForegroundColor Green
Write-Host "   → http://192.168.0.185:8500" -ForegroundColor Yellow

Write-Host "
🌐 STEP 2: CREATE TUNNEL FOR 4G" -ForegroundColor Cyan

Write-Host "
Choose your tunnel option:

Option A: ngrok (Recommended)
  1. Go to https://ngrok.com/download
  2. Download ngrok for Windows
  3. Open new PowerShell and run: ngrok http 8500
  4. Copy the https://xxx.ngrok.io URL

Option B: localtunnel (No signup needed)
  1. Open new PowerShell (admin)
  2. Run: npm install -g localtunnel
  3. Run: lt --port 8500
  4. Copy the provided https://xxx.loca.lt URL

Option C: Cloudflare Tunnel (No signup needed)
  1. Open new PowerShell and run: 
     choco install cloudflared -y
  2. Run: cloudflared tunnel --url http://localhost:8500
  3. Copy the https://xxx.trycloudflare.com URL
" -ForegroundColor Yellow

Write-Host "
📱 On your 4G phone, use the public URL provided by your tunnel service" -ForegroundColor Cyan

Write-Host "
Waiting for tunnel... Press Ctrl+C to stop." -ForegroundColor Green

# Keep running
while($true) { Start-Sleep -Seconds 1 }
