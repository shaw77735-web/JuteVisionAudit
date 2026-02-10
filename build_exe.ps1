# Build script to create a standalone EXE using PyInstaller
# Usage: Open PowerShell in project root and run: .\build_exe.ps1

python -m pip install --upgrade pip
pip install pyinstaller

# Create a one-folder build with hidden console
pyinstaller --noconfirm --onefile --name JuteVisionAuditor jute_test.py

Write-Host "Build complete. Check the dist\JuteVisionAuditor.exe"