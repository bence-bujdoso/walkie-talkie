#!/usr/bin/env python3
"""
TK11 CPS .dat File Patcher
==========================
Modifies the TX mask in a TK11 CPS .dat file to enable USB TX mode.

Usage:
    python patch_tk11_cps_dat.py <input.dat>
    python patch_tk11_cps_dat.py TK11_BACKUP.dat

Author: Claude Code
Date: 2025-11-06
"""

import sys
import os
from pathlib import Path
import struct

# Configuration
TX_MASK_OFFSET = 0x314D  # Offset of TX mask in memory
ORIGINAL_VALUE = 0x03    # Expected original value (USB TX disabled)
NEW_VALUE = 0x17         # New value (USB TX enabled) - 0x01 + 0x02 + 0x04 + 0x10

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print()
    print(Colors.BOLD + Colors.CYAN + "="*80 + Colors.END)
    print(Colors.BOLD + Colors.CYAN + text.center(80) + Colors.END)
    print(Colors.BOLD + Colors.CYAN + "="*80 + Colors.END)
    print()

def print_success(text):
    """Print success message"""
    print(Colors.GREEN + "✅ " + text + Colors.END)

def print_error(text):
    """Print error message"""
    print(Colors.RED + "❌ " + text + Colors.END)

def print_info(text):
    """Print info message"""
    print(Colors.BLUE + "ℹ️  " + text + Colors.END)

def print_warning(text):
    """Print warning message"""
    print(Colors.YELLOW + "⚠️  " + text + Colors.END)

def validate_file(file_path):
    """Validate the input file"""
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return False

    file_size = os.path.getsize(file_path)
    if file_size < TX_MASK_OFFSET + 1:
        print_error(f"File too small! Size: {file_size} bytes, need at least {TX_MASK_OFFSET + 1} bytes")
        return False

    return True

def read_current_value(data, offset):
    """Read and display current value at offset"""
    current_value = data[offset]

    print(f"Offset: 0x{offset:04X} ({offset} decimal)")
    print(f"Current value: 0x{current_value:02X} ({current_value} decimal)")
    print(f"Binary: {format(current_value, '08b')}")

    # Interpret the value
    print()
    print("TX Mode Status:")
    if current_value & 0x01:
        print("  ✅ FM mode TX: ENABLED")
    else:
        print("  ❌ FM mode TX: DISABLED")

    if current_value & 0x02:
        print("  ✅ AIR mode TX: ENABLED")
    else:
        print("  ❌ AIR mode TX: DISABLED")

    if current_value & 0x04:
        print("  " + (Colors.GREEN + "✅" if current_value & 0x04 else Colors.RED + "❌") +
              " USB mode TX: " + ("ENABLED" if current_value & 0x04 else "DISABLED") + Colors.END)

    if current_value & 0x10:
        print("  ✅ WFM mode TX: ENABLED")
    else:
        print("  ❌ WFM mode TX: DISABLED")

    return current_value

def show_new_value(new_value):
    """Show what the new value will be"""
    print()
    print(f"New value: 0x{new_value:02X} ({new_value} decimal)")
    print(f"Binary: {format(new_value, '08b')}")

    print()
    print("After patching:")
    if new_value & 0x01:
        print("  ✅ FM mode TX: ENABLED")
    else:
        print("  ❌ FM mode TX: DISABLED")

    if new_value & 0x02:
        print("  ✅ AIR mode TX: ENABLED")
    else:
        print("  ❌ AIR mode TX: DISABLED")

    if new_value & 0x04:
        print(Colors.GREEN + "  ✅ USB mode TX: ENABLED ← VÁLTOZIK!" + Colors.END)
    else:
        print("  ❌ USB mode TX: DISABLED")

    if new_value & 0x10:
        print("  ✅ WFM mode TX: ENABLED")
    else:
        print("  ❌ WFM mode TX: DISABLED")

def patch_dat_file(input_file):
    """Main patching function"""

    print_header("TK11 CPS .dat File Patcher")

    # Validate file
    print_info(f"Input file: {input_file}")
    if not validate_file(input_file):
        return False

    file_size = os.path.getsize(input_file)
    print_success(f"File valid! Size: {file_size:,} bytes")

    # Read file
    print()
    print_info("Reading file...")
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    print_success(f"Read {len(data):,} bytes")

    # Show current value
    print()
    print_header("Current TX Mask Configuration")
    current_value = read_current_value(data, TX_MASK_OFFSET)

    # Check if already patched
    if current_value == NEW_VALUE:
        print()
        print_warning("File appears to be already patched!")
        print_info("USB TX is already ENABLED (0x04 bit is set)")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print_info("Aborted by user")
            return False

    # Show what will change
    print_header("Planned Changes")
    show_new_value(NEW_VALUE)

    # Confirm
    print()
    print(Colors.BOLD + "⚠️  This will modify the .dat file!" + Colors.END)
    response = input("Continue with patching? (y/n): ").strip().lower()
    if response != 'y':
        print_info("Aborted by user")
        return False

    # Apply patch
    print()
    print_info("Applying patch...")
    data[TX_MASK_OFFSET] = NEW_VALUE

    # Generate output filename
    input_path = Path(input_file)
    output_file = input_path.parent / (input_path.stem + "_PATCHED" + input_path.suffix)

    # Save patched file
    print_info(f"Saving patched file: {output_file}")
    with open(output_file, 'wb') as f:
        f.write(data)

    print_success(f"Patched file saved: {output_file}")
    print_success(f"Size: {len(data):,} bytes")

    # Verify
    print()
    print_info("Verifying patch...")
    with open(output_file, 'rb') as f:
        verify_data = bytearray(f.read())

    if verify_data[TX_MASK_OFFSET] == NEW_VALUE:
        print_success("Patch verified successfully!")
    else:
        print_error("Verification failed!")
        return False

    # Success summary
    print_header("Patch Completed Successfully!")

    print(Colors.GREEN + Colors.BOLD + "✅ USB TX mode is now ENABLED!" + Colors.END)
    print()
    print("Next steps:")
    print("  1. Open TK11.exe (original or patched version)")
    print("  2. Connect your radio in NORMAL mode (not bootloader)")
    print("  3. Click 'Write' or 'Upload to radio'")
    print(f"  4. Select the patched file: {output_file.name}")
    print("  5. Wait for completion")
    print("  6. Test USB TX mode - it should work now!")
    print()
    print(Colors.BOLD + "⚠️  IMPORTANT: Keep the original backup!" + Colors.END)
    print(f"     Original: {input_file}")
    print(f"     Patched: {output_file}")
    print()
    print("If you need to restore:")
    print("  - Just write the original .dat file back to the radio")
    print()

    return True

def main():
    """Main entry point"""

    # Check arguments
    if len(sys.argv) < 2:
        print_header("TK11 CPS .dat File Patcher")
        print("Usage:")
        print(f"  {sys.argv[0]} <input.dat>")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} TK11_BACKUP.dat")
        print()
        print("What this does:")
        print("  - Reads your TK11 CPS backup (.dat file)")
        print("  - Modifies the TX mask at offset 0x314D")
        print("  - Changes 0x03 → 0x17 (enables USB TX)")
        print("  - Saves as <filename>_PATCHED.dat")
        print()
        print("How to get the .dat file:")
        print("  1. Open TK11.exe")
        print("  2. Connect radio (normal mode)")
        print("  3. Click 'Read' or 'Download from radio'")
        print("  4. Save as TK11_BACKUP.dat")
        print("  5. Run this script on that file")
        print()
        return 1

    input_file = sys.argv[1]

    try:
        success = patch_dat_file(input_file)
        return 0 if success else 1
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
