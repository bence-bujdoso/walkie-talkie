#!/usr/bin/env python3
"""Verify the checksum-fixed firmware has correct patch and checksum"""

from pathlib import Path
import struct

def verify_firmware(firmware_path):
    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print(f"VERIFYING: {firmware_path.name}")
    print("="*80)

    # Check 1: TX patch at offset 0x314D
    tx_offset = 0x0000314D
    tx_byte = data[tx_offset]

    print(f"\n[1] TX Enable Patch (offset 0x{tx_offset:08X}):")
    print(f"    Value: 0x{tx_byte:02X} (binary: {tx_byte:08b})")

    if tx_byte == 0x13:
        print("    [OK] TX patch present (USB mode enabled)")
    elif tx_byte == 0x03:
        print("    [FAIL] TX patch NOT applied (USB mode disabled)")
    else:
        print(f"    [WARN] Unexpected value (expected 0x13)")

    # Check 2: Checksum in last 4 bytes
    stored_checksum = struct.unpack('<I', data[-4:])[0]
    calculated_checksum = sum(data[:-4]) & 0xFFFFFFFF

    print(f"\n[2] Checksum Validation (last 4 bytes):")
    print(f"    Stored:     0x{stored_checksum:08X}")
    print(f"    Calculated: 0x{calculated_checksum:08X}")

    if stored_checksum == calculated_checksum:
        print("    [OK] Checksum matches")
    else:
        print("    [FAIL] Checksum mismatch")

    # Overall result
    print("\n" + "="*80)
    if tx_byte == 0x13 and stored_checksum == calculated_checksum:
        print("VERIFICATION PASSED!")
        print("="*80)
        print("\nThis firmware is ready to flash:")
        print("  - USB TX enabled")
        print("  - Checksum correct")
        print("  - TK11.exe should accept it")
        return True
    else:
        print("VERIFICATION FAILED!")
        print("="*80)
        print("\nProblems found:")
        if tx_byte != 0x13:
            print("  - TX patch missing or incorrect")
        if stored_checksum != calculated_checksum:
            print("  - Checksum incorrect")
        return False

if __name__ == "__main__":
    print("\nVerifying CHECKSUM-FIXED firmware...\n")
    fixed = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin")

    if not fixed.exists():
        print(f"ERROR: File not found: {fixed}")
    else:
        verify_firmware(fixed)

    print("\n\nFor comparison, verifying ORIGINAL patched firmware...\n")
    original_patch = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin")

    if original_patch.exists():
        verify_firmware(original_patch)
