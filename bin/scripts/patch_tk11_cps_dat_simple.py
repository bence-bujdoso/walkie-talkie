#!/usr/bin/env python3
"""
TK11 CPS .dat File Patcher - Simple Version
============================================
Simple, non-interactive version for batch processing.

Usage:
    python patch_tk11_cps_dat_simple.py <input.dat> [output.dat]

Example:
    python patch_tk11_cps_dat_simple.py TK11_BACKUP.dat
    python patch_tk11_cps_dat_simple.py TK11_BACKUP.dat TK11_PATCHED.dat

Author: Claude Code
Date: 2025-11-06
"""

import sys
import os
from pathlib import Path

# Configuration
TX_MASK_OFFSET = 0x314D  # Offset of TX mask in memory
NEW_VALUE = 0x13         # New value (USB TX enabled)

def patch_dat_file(input_file, output_file=None):
    """Patch the .dat file"""

    # Check input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: File not found: {input_file}")
        return False

    # Read file
    print(f"Reading: {input_file}")
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    print(f"Size: {len(data)} bytes")

    # Check offset is within bounds
    if TX_MASK_OFFSET >= len(data):
        print(f"ERROR: Offset 0x{TX_MASK_OFFSET:04X} is beyond file size!")
        return False

    # Show current value
    current_value = data[TX_MASK_OFFSET]
    print(f"Current TX mask: 0x{current_value:02X} (binary: {format(current_value, '08b')})")

    # Check if already patched
    if current_value == NEW_VALUE:
        print(f"WARNING: File appears to be already patched (value is already 0x{NEW_VALUE:02X})")

    # Apply patch
    data[TX_MASK_OFFSET] = NEW_VALUE
    print(f"New TX mask: 0x{NEW_VALUE:02X} (binary: {format(NEW_VALUE, '08b')})")

    # Generate output filename if not specified
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / (input_path.stem + "_PATCHED" + input_path.suffix))

    # Save patched file
    print(f"Writing: {output_file}")
    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"SUCCESS: Patched file saved!")
    print()
    print("Next steps:")
    print("  1. Open TK11.exe")
    print("  2. Connect radio (normal mode)")
    print("  3. Click 'Write' / 'Upload to radio'")
    print(f"  4. Select: {output_file}")
    print("  5. Wait for completion")
    print("  6. Test USB TX mode!")
    print()

    return True

def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        print("TK11 CPS .dat File Patcher - Simple Version")
        print()
        print("Usage:")
        print(f"  {sys.argv[0]} <input.dat> [output.dat]")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} TK11_BACKUP.dat")
        print(f"  {sys.argv[0]} TK11_BACKUP.dat TK11_PATCHED.dat")
        print()
        return 1

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        success = patch_dat_file(input_file, output_file)
        return 0 if success else 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
