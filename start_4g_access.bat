@echo off
REM ============================================================================
REM  JuteVision 4G Live Tunnel - Easy Setup
REM  Requires: Node.js installed
REM ============================================================================

cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     JuteVision - 4G Live Access (Phone + Wi-Fi Both Work)     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Kill existing processes
taskkill /F /IM streamlit.exe 2>NUL
taskkill /F /IM node.exe 2>NUL
timeout /t 2 /nobreak

REM Start Streamlit
echo.
echo 📍 STARTING STREAMLIT ON PORT 8500...
echo.
cd /d "C:\Users\AFTAB\Desktop\New folder\JuteVision"
call .\venv\Scripts\activate.bat

REM Check if Node is installed for localtunnel
where node >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Node.js not found. You need Node.js for localtunnel.
    echo.
    echo Install from: https://nodejs.org/
    echo Then run this script again.
    pause
    exit /b 1
)

REM Start Streamlit in background
start "" .\venv\Scripts\streamlit.exe run jute_test.py --server.port=8500 --server.address=0.0.0.0 --server.enableCORS=false

timeout /t 5 /nobreak

echo ✅ Streamlit is running!
echo.
echo ════════════════════════════════════════════════════════════════
echo 📱 LOCAL ACCESS (Same Wi-Fi):
echo    → http://192.168.0.185:8500
echo ════════════════════════════════════════════════════════════════
echo.
echo.
echo 🌐 CREATING 4G TUNNEL...
echo.

REM Install and run localtunnel
npm install -g localtunnel 2>NUL
call npx localtunnel --port 8500

pause
