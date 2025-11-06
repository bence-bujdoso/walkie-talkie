#!/usr/bin/env python3
"""
TK11 Patch Verifier
===================
Verifies if the TX mask patch is present in a .dat file.

Usage:
    python verify_tk11_patch.py <file.dat>
"""

import sys
import os

TX_MASK_OFFSET = 0x314D
EXPECTED_PATCHED = 0x13
EXPECTED_ORIGINAL = 0x03

def verify_patch(file_path):
    """Verify if the patch is present"""

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    # Read file
    with open(file_path, 'rb') as f:
        data = f.read()

    file_size = len(data)
    print(f"File: {file_path}")
    print(f"Size: {file_size:,} bytes")
    print()

    # Check offset
    if TX_MASK_OFFSET >= file_size:
        print(f"❌ ERROR: Offset 0x{TX_MASK_OFFSET:04X} is beyond file size!")
        return False

    # Read value at offset
    value = data[TX_MASK_OFFSET]

    print(f"TX Mask at offset 0x{TX_MASK_OFFSET:04X} ({TX_MASK_OFFSET} decimal):")
    print(f"  Value: 0x{value:02X} ({value} decimal)")
    print(f"  Binary: {format(value, '08b')}")
    print()

    # Check if patched
    if value == EXPECTED_PATCHED:
        print("✅ FILE IS PATCHED!")
        print(f"   Value is 0x{EXPECTED_PATCHED:02X} - USB TX should be ENABLED")
    elif value == EXPECTED_ORIGINAL:
        print("❌ FILE IS NOT PATCHED!")
        print(f"   Value is 0x{EXPECTED_ORIGINAL:02X} - USB TX is DISABLED")
    else:
        print(f"⚠️  UNKNOWN VALUE: 0x{value:02X}")
        print("   This is neither the original nor the patched value!")

    print()

    # Show bits
    print("Bit breakdown:")
    if value & 0x01:
        print("  Bit 0 (0x01): ✅ SET - FM mode TX enabled")
    else:
        print("  Bit 0 (0x01): ❌ CLEAR - FM mode TX disabled")

    if value & 0x02:
        print("  Bit 1 (0x02): ✅ SET - AIR mode TX enabled")
    else:
        print("  Bit 1 (0x02): ❌ CLEAR - AIR mode TX disabled")

    if value & 0x04:
        print("  Bit 2 (0x04): ✅ SET - USB mode TX enabled")
    else:
        print("  Bit 2 (0x04): ❌ CLEAR - USB mode TX disabled")

    if value & 0x08:
        print("  Bit 3 (0x08): ✅ SET")
    else:
        print("  Bit 3 (0x08): ❌ CLEAR")

    if value & 0x10:
        print("  Bit 4 (0x10): ✅ SET - WFM mode TX enabled")
    else:
        print("  Bit 4 (0x10): ❌ CLEAR - WFM mode TX disabled")

    print()

    # Show surrounding bytes for context
    start = max(0, TX_MASK_OFFSET - 8)
    end = min(file_size, TX_MASK_OFFSET + 9)

    print(f"Surrounding bytes (0x{start:04X} - 0x{end-1:04X}):")
    hex_str = ""
    ascii_str = ""
    for i in range(start, end):
        if i == TX_MASK_OFFSET:
            hex_str += f"[{data[i]:02X}] "
            ascii_str += f"[{chr(data[i]) if 32 <= data[i] < 127 else '.'}]"
        else:
            hex_str += f"{data[i]:02X} "
            ascii_str += chr(data[i]) if 32 <= data[i] < 127 else '.'

    print(f"  Hex: {hex_str}")
    print(f"  ASCII: {ascii_str}")
    print()
    print("  [XX] = TX mask byte")

    return value == EXPECTED_PATCHED

def main():
    if len(sys.argv) < 2:
        print("TK11 Patch Verifier")
        print()
        print("Usage:")
        print(f"  {sys.argv[0]} <file.dat>")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} TK11_BACKUP_PATCHED.dat")
        print()
        return 1

    file_path = sys.argv[1]

    try:
        is_patched = verify_patch(file_path)

        print()
        print("="*60)
        if is_patched:
            print("✅ Verification: PATCH IS PRESENT")
        else:
            print("❌ Verification: PATCH IS NOT PRESENT")
        print("="*60)

        return 0 if is_patched else 1

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
