# TK11 Firmware Patcher - PowerShell Script
# Automatically creates all 8 patched firmware variants

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  TK11 USB TX Unlock - Firmware Patcher" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check for original firmware
$originalFirmware = "bin\original\TK11_v5.00.09_ENG.bin"
$originalExe = "bin\original\TK11.exe"

if (-Not (Test-Path $originalFirmware)) {
    Write-Host "[ERROR] Original firmware not found!" -ForegroundColor Red
    Write-Host "Expected: $originalFirmware" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download:" -ForegroundColor Yellow
    Write-Host "  https://itistesla.com/ai/TK11_v5.00.09_ENG.bin" -ForegroundColor Yellow
    Write-Host "  https://itistesla.com/ai/TK11.exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "And place them in: bin\original\" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Found original firmware: $originalFirmware" -ForegroundColor Green

if (-Not (Test-Path $originalExe)) {
    Write-Host "[WARNING] TK11.exe not found in bin\original\" -ForegroundColor Yellow
    Write-Host "Expected: $originalExe" -ForegroundColor Yellow
}

# Copy firmware to root for processing
Write-Host "[*] Copying firmware to workspace..." -ForegroundColor Cyan
Copy-Item $originalFirmware "TK11_v5.00.09_ENG.bin" -Force

# Check for Python
Write-Host "[*] Checking for Python..." -ForegroundColor Cyan
$pythonCmd = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} else {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.x from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Found Python: $pythonCmd" -ForegroundColor Green

# Run the patcher script
Write-Host ""
Write-Host "[*] Running firmware patcher..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

& $pythonCmd create_perfect_firmware.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Firmware patcher failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] All firmware variants created!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output directory: patched_firmware_final\" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Patch TK11.exe using dnSpy" -ForegroundColor Yellow
Write-Host "   Instructions: bin\scripts\patch_tk11_updata_method.cs" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Test firmware variants:" -ForegroundColor Yellow
Write-Host "   - Open patched TK11.exe" -ForegroundColor Yellow
Write-Host "   - Load: patched_firmware_final\TK11_PATCHED_v3_minimal.bin" -ForegroundColor Yellow
Write-Host "   - Flash to radio" -ForegroundColor Yellow
Write-Host ""
Write-Host "Good luck! 73! 📻" -ForegroundColor Cyan