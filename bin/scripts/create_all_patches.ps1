# TK11 Complete Patcher - Master Script (PowerShell)
# ====================================================

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BinDir = Split-Path -Parent $ScriptDir
$OriginalDir = Join-Path $BinDir "original"
$FirmwareDir = Join-Path $BinDir "patched_firmware"
$SoftwareDir = Join-Path $BinDir "patched_software"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TK11 Complete Patcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for original files
Write-Host "[*] Checking for original files..." -ForegroundColor Yellow
Write-Host ""

$FirmwareFile = Get-ChildItem -Path $OriginalDir -Filter "TK11*.bin" -File -ErrorAction SilentlyContinue | Select-Object -First 1
$TK11Exe = Get-ChildItem -Path $OriginalDir -Filter "TK11.exe" -File -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $FirmwareFile) {
    Write-Host "[!] ERROR: No firmware file found in $OriginalDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download and place the firmware file:" -ForegroundColor Yellow
    Write-Host "  URL: https://itistesla.com/ai/TK11_v5.00.09_ENG.bin"
    Write-Host "  Location: $OriginalDir\"
    Write-Host ""
    exit 1
}

if (-not $TK11Exe) {
    Write-Host "[!] ERROR: TK11.exe not found in $OriginalDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download and place TK11.exe:" -ForegroundColor Yellow
    Write-Host "  URL: https://itistesla.com/ai/TK11.exe"
    Write-Host "  Location: $OriginalDir\"
    Write-Host ""
    exit 1
}

Write-Host "[✓] Found firmware: $($FirmwareFile.Name)" -ForegroundColor Green
Write-Host "[✓] Found TK11.exe: $($TK11Exe.Name)" -ForegroundColor Green
Write-Host ""

# Generate patched firmware
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Generating Patched Firmware" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PythonScript = Join-Path $ScriptDir "generate_patched_firmware.py"

try {
    python $PythonScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[✓] Patched firmware variants created successfully!" -ForegroundColor Green
    } else {
        throw "Python script returned error code: $LASTEXITCODE"
    }
} catch {
    Write-Host ""
    Write-Host "[!] ERROR: Firmware patching failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Prepare software patching instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 2: Patching TK11.exe" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] TK11.exe must be patched manually using dnSpy" -ForegroundColor Yellow
Write-Host ""
Write-Host "Instructions:"
Write-Host "  1. Open dnSpy (Windows tool)"
Write-Host "  2. Load TK11.exe from: $OriginalDir\"
Write-Host "  3. Follow instructions in: $ScriptDir\patch_tk11_updata_method.cs"
Write-Host "  4. Save patched version to: $SoftwareDir\TK11_PATCHED.exe"
Write-Host ""
Write-Host "Detailed guide: See README.md in bin\ folder"
Write-Host ""

# Copy original files to software dir for reference
New-Item -ItemType Directory -Force -Path $SoftwareDir | Out-Null
Copy-Item -Path $TK11Exe.FullName -Destination (Join-Path $SoftwareDir "TK11_ORIGINAL.exe") -Force
Write-Host "[✓] Original TK11.exe copied to: $SoftwareDir\TK11_ORIGINAL.exe" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[✓] Firmware patching: COMPLETE" -ForegroundColor Green
Write-Host "    Location: $FirmwareDir\"
Write-Host ""
Write-Host "[!] Software patching: MANUAL STEP REQUIRED" -ForegroundColor Yellow
Write-Host "    See: $ScriptDir\patch_tk11_updata_method.cs"
Write-Host ""
Write-Host "[*] Next steps:" -ForegroundColor Cyan
Write-Host "    1. Patch TK11.exe using dnSpy (see instructions)"
Write-Host "    2. Test with TK11_PATCHED_v3_minimal.bin first"
Write-Host "    3. Flash to radio"
Write-Host "    4. Test USB TX mode"
Write-Host ""
Write-Host "Good luck! 73! 📻" -ForegroundColor Green
Write-Host ""
