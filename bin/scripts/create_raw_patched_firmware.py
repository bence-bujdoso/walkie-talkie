#!/usr/bin/env python3
"""
TK11 RAW Firmware Patcher
Creates a RAW (decrypted) patched firmware for direct flashing

Since the encrypted/wrapped firmware doesn't work, we'll create a raw version
that can be flashed directly with the patched TK11.exe
"""

import struct
import os
from pathlib import Path

def create_raw_patched_firmware(original_firmware_path, output_path):
    """
    Create a raw patched firmware by:
    1. Reading the original firmware
    2. Assuming it's already decrypted when loaded by TK11.exe
    3. Applying the USB TX patch
    4. Saving as raw binary
    """

    print("="*80)
    print("TK11 RAW FIRMWARE PATCHER")
    print("="*80)
    print()

    # Read original firmware
    with open(original_firmware_path, 'rb') as f:
        firmware_data = bytearray(f.read())

    print(f"[+] Loaded original firmware: {len(firmware_data)} bytes")

    # USB TX unlock offset
    TX_MASK_OFFSET = 0x314D

    # Check if offset is within bounds
    if TX_MASK_OFFSET >= len(firmware_data):
        print(f"[!] ERROR: TX mask offset 0x{TX_MASK_OFFSET:04X} is beyond firmware size!")
        return False

    # Show original value
    original_value = firmware_data[TX_MASK_OFFSET]
    print(f"[*] Original TX mask at 0x{TX_MASK_OFFSET:04X}: 0x{original_value:02X}")
    print(f"    Binary: {bin(original_value)}")

    # Apply USB TX unlock
    firmware_data[TX_MASK_OFFSET] = 0x13

    new_value = firmware_data[TX_MASK_OFFSET]
    print(f"[+] Patched TX mask to: 0x{new_value:02X}")
    print(f"    Binary: {bin(new_value)}")
    print(f"    Effect: USB (0x04) mode TX now ENABLED")
    print()

    # Save raw patched firmware
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(firmware_data)

    print(f"[+] Created RAW patched firmware: {output_path}")
    print(f"    Size: {len(firmware_data)} bytes")
    print()

    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print()
    print("1. Use TK11_PATCHED.exe (Level 1-2 bypass)")
    print("2. Load the RAW patched firmware (this file)")
    print("3. Flash to radio")
    print()
    print("The TK11.exe will:")
    print("- Try PareUpdataFile() → FAIL (wrong format)")
    print("- Try PareUpdataFile1() → FAIL (wrong format)")
    print("- Use File.ReadAllBytes() → SUCCESS (bypass works!)")
    print("- Send raw bytes directly to bootloader")
    print()
    print("Expected result:")
    print("✅ Flash should complete successfully")
    print("✅ USB TX unlock should work")
    print()

    return True

def main():
    """Main entry point"""

    # Paths
    script_dir = Path(__file__).parent.parent
    original_firmware = script_dir / "bin" / "original" / "TK11_v5.00.09_ENG.bin"
    output_firmware = script_dir / "bin" / "patched_firmware" / "TK11_PATCHED_RAW.bin"

    # Check if original exists
    if not original_firmware.exists():
        print(f"[!] ERROR: Original firmware not found!")
        print(f"[!] Expected location: {original_firmware}")
        print()
        print("Please download the original firmware:")
        print("  URL: https://itistesla.com/ai/TK11_v5.00.09_ENG.bin")
        print(f"  Place it in: {original_firmware.parent}")
        return 1

    # Create raw patched firmware
    success = create_raw_patched_firmware(str(original_firmware), str(output_firmware))

    if success:
        print("[✓] Done! Raw patched firmware is ready to test.")
        print()
        print("⚠️  IMPORTANT:")
        print("This is the SAME SIZE as the original (357,976 bytes)")
        print("But with 1 byte changed for USB TX unlock")
        print()
        print("If this ALSO fails with 'Write Fail':")
        print("→ The firmware is encrypted and needs to be decrypted first")
        print("→ We'll need to extract the decryption algorithm from TK11.exe")
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())
