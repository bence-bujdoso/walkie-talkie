#!/bin/bash
# TK11 Firmware Patcher - Bash Script
# Automatically creates all 8 patched firmware variants

echo "================================================================"
echo "  TK11 USB TX Unlock - Firmware Patcher"
echo "================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check for original firmware
ORIGINAL_FIRMWARE="bin/original/TK11_v5.00.09_ENG.bin"
ORIGINAL_EXE="bin/original/TK11.exe"

if [ ! -f "$ORIGINAL_FIRMWARE" ]; then
    echo -e "${RED}[ERROR] Original firmware not found!${NC}"
    echo "Expected: $ORIGINAL_FIRMWARE"
    echo ""
    echo -e "${YELLOW}Please download:${NC}"
    echo "  https://itistesla.com/ai/TK11_v5.00.09_ENG.bin"
    echo "  https://itistesla.com/ai/TK11.exe"
    echo ""
    echo -e "${YELLOW}And place them in: bin/original/${NC}"
    exit 1
fi

echo -e "${GREEN}[OK] Found original firmware: $ORIGINAL_FIRMWARE${NC}"

if [ ! -f "$ORIGINAL_EXE" ]; then
    echo -e "${YELLOW}[WARNING] TK11.exe not found in bin/original/${NC}"
    echo "Expected: $ORIGINAL_EXE"
fi

# Copy firmware to root for processing
echo -e "${CYAN}[*] Copying firmware to workspace...${NC}"
cp "$ORIGINAL_FIRMWARE" "TK11_v5.00.09_ENG.bin"

# Check for Python
echo -e "${CYAN}[*] Checking for Python...${NC}"
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[ERROR] Python not found!${NC}"
    echo -e "${YELLOW}Please install Python 3.x${NC}"
    exit 1
fi

echo -e "${GREEN}[OK] Found Python: $PYTHON_CMD${NC}"

# Run the patcher script
echo ""
echo -e "${CYAN}[*] Running firmware patcher...${NC}"
echo "================================================================"
echo ""

$PYTHON_CMD create_perfect_firmware.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR] Firmware patcher failed!${NC}"
    exit 1
fi

echo ""
echo "================================================================"
echo -e "${GREEN}[SUCCESS] All firmware variants created!${NC}"
echo "================================================================"
echo ""
echo -e "${GREEN}Output directory: patched_firmware_final/${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${YELLOW}1. Patch TK11.exe using dnSpy (Windows only)${NC}"
echo -e "${YELLOW}   Instructions: bin/scripts/patch_tk11_updata_method.cs${NC}"
echo ""
echo -e "${YELLOW}2. Test firmware variants:${NC}"
echo -e "${YELLOW}   - Open patched TK11.exe${NC}"
echo -e "${YELLOW}   - Load: patched_firmware_final/TK11_PATCHED_v3_minimal.bin${NC}"
echo -e "${YELLOW}   - Flash to radio${NC}"
echo ""
echo -e "${CYAN}Good luck! 73! 📻${NC}"