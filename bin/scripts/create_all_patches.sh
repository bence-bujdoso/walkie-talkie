#!/bin/bash
# TK11 Complete Patcher - Master Script
# ======================================

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIN_DIR="$(dirname "$SCRIPT_DIR")"
ORIGINAL_DIR="$BIN_DIR/original"
FIRMWARE_DIR="$BIN_DIR/patched_firmware"
SOFTWARE_DIR="$BIN_DIR/patched_software"

echo "========================================"
echo "TK11 Complete Patcher"
echo "========================================"
echo ""

# Check for original files
echo "[*] Checking for original files..."
echo ""

FIRMWARE_FILE=$(find "$ORIGINAL_DIR" -name "TK11*.bin" -type f 2>/dev/null | head -1)
TK11_EXE=$(find "$ORIGINAL_DIR" -name "TK11.exe" -type f 2>/dev/null | head -1)

if [ -z "$FIRMWARE_FILE" ]; then
    echo "[!] ERROR: No firmware file found in $ORIGINAL_DIR"
    echo ""
    echo "Please download and place the firmware file:"
    echo "  URL: https://itistesla.com/ai/TK11_v5.00.09_ENG.bin"
    echo "  Location: $ORIGINAL_DIR/"
    echo ""
    exit 1
fi

if [ -z "$TK11_EXE" ]; then
    echo "[!] ERROR: TK11.exe not found in $ORIGINAL_DIR"
    echo ""
    echo "Please download and place TK11.exe:"
    echo "  URL: https://itistesla.com/ai/TK11.exe"
    echo "  Location: $ORIGINAL_DIR/"
    echo ""
    exit 1
fi

echo "[✓] Found firmware: $(basename "$FIRMWARE_FILE")"
echo "[✓] Found TK11.exe: $(basename "$TK11_EXE")"
echo ""

# Generate patched firmware
echo "========================================"
echo "Step 1: Generating Patched Firmware"
echo "========================================"
echo ""

python3 "$SCRIPT_DIR/generate_patched_firmware.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "[✓] Patched firmware variants created successfully!"
else
    echo ""
    echo "[!] ERROR: Firmware patching failed!"
    exit 1
fi

# Prepare software patching instructions
echo ""
echo "========================================"
echo "Step 2: Patching TK11.exe"
echo "========================================"
echo ""
echo "[*] TK11.exe must be patched manually using dnSpy"
echo ""
echo "Instructions:"
echo "  1. Open dnSpy (Windows tool)"
echo "  2. Load TK11.exe from: $ORIGINAL_DIR/"
echo "  3. Follow instructions in: $SCRIPT_DIR/patch_tk11_updata_method.cs"
echo "  4. Save patched version to: $SOFTWARE_DIR/TK11_PATCHED.exe"
echo ""
echo "Detailed guide: See README.md in bin/ folder"
echo ""

# Copy original files to software dir for reference
mkdir -p "$SOFTWARE_DIR"
cp "$TK11_EXE" "$SOFTWARE_DIR/TK11_ORIGINAL.exe"
echo "[✓] Original TK11.exe copied to: $SOFTWARE_DIR/TK11_ORIGINAL.exe"
echo ""

# Summary
echo "========================================"
echo "Summary"
echo "========================================"
echo ""
echo "[✓] Firmware patching: COMPLETE"
echo "    Location: $FIRMWARE_DIR/"
echo ""
echo "[!] Software patching: MANUAL STEP REQUIRED"
echo "    See: $SCRIPT_DIR/patch_tk11_updata_method.cs"
echo ""
echo "[*] Next steps:"
echo "    1. Patch TK11.exe using dnSpy (see instructions)"
echo "    2. Test with TK11_PATCHED_v3_minimal.bin first"
echo "    3. Flash to radio"
echo "    4. Test USB TX mode"
echo ""
echo "Good luck! 73! 📻"
echo ""
