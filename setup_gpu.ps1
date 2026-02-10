# JuteVision - One-time GPU (CUDA) setup
# Run this once to switch from CPU to GPU. Requires NVIDIA GPU + drivers.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "JuteVision GPU Setup" -ForegroundColor Cyan
Write-Host ""

# Check nvidia-smi
try {
    $null = nvidia-smi 2>$null
    Write-Host "[OK] NVIDIA driver found" -ForegroundColor Green
} catch {
    Write-Host "[!] nvidia-smi not found. Install/update NVIDIA drivers first." -ForegroundColor Yellow
    Write-Host "    https://www.nvidia.com/Download/index.aspx" -ForegroundColor Gray
    exit 1
}

# Use existing venv or create
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Creating venv..." -ForegroundColor Gray
    python -m venv venv
}
& ".\venv\Scripts\Activate.ps1"

# Uninstall CPU PyTorch
Write-Host "Removing CPU PyTorch..." -ForegroundColor Gray
pip uninstall -y torch torchvision 2>$null

# Install PyTorch with CUDA 12.1 (works for most RTX 30xx)
Write-Host "Installing PyTorch with CUDA (this may take a few minutes)..." -ForegroundColor Gray
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify
Write-Host ""
$check = python -c "import torch; print('OK' if torch.cuda.is_available() else 'FAIL')"
if ($check -match "OK") {
    $name = python -c "import torch; print(torch.cuda.get_device_name(0))"
    Write-Host "[OK] GPU ready: $name" -ForegroundColor Green
} else {
    Write-Host "[!] CUDA still not available. Try updating NVIDIA drivers or use CUDA 11.8:" -ForegroundColor Yellow
    Write-Host "    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Run the app: .\venv\Scripts\Activate.ps1; python jute_test.py" -ForegroundColor Cyan
streamlit run jute_test.py
