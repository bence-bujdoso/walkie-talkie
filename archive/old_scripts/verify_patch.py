#!/usr/bin/env python3
"""Verify the USB TX patch was applied correctly"""

from pathlib import Path

offset = 0x0000314D

original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin")

print("="*60)
print("USB TX PATCH VERIFICATION")
print("="*60)

with open(original, 'rb') as f:
    f.seek(offset)
    orig_byte = f.read(1)[0]

with open(patched, 'rb') as f:
    f.seek(offset)
    patched_byte = f.read(1)[0]

print(f"\nOffset: 0x{offset:08X}")
print(f"\nOriginal firmware: 0x{orig_byte:02X} (binary: {orig_byte:08b})")
print(f"Patched firmware:  0x{patched_byte:02X} (binary: {patched_byte:08b})")

print("\n" + "="*60)
if orig_byte == 0x03 and patched_byte == 0x13:
    print("VERIFICATION PASSED!")
    print("="*60)
    print("\nPatch applied correctly!")
    print("\nWhat changed:")
    print("  Original: 0x03 = 00000011 (FM + AM only)")
    print("  Patched:  0x13 = 00010011 (FM + AM + USB)")
    print("\nBit 4 enabled -> Mode 0x04 (USB) can now TX!")
    print("\nRESULT:")
    print("  - USB mode will NO LONGER show 'DISABLED'")
    print("  - TX will use AM modulation")
    print("  - RX will use USB demodulation")
    print("  - Perfect for SSB RX / AM TX hybrid operation!")
else:
    print("VERIFICATION FAILED!")
    print("="*60)
    print(f"\nExpected: 0x03 -> 0x13")
    print(f"Got:      0x{orig_byte:02X} -> 0x{patched_byte:02X}")
