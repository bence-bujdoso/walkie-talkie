#!/usr/bin/env python3
"""
TK11 Firmware Patcher - Enable USB Mode (0x04) TX

This patch allows mode 0x04 (USB) to transmit.
Result: RX=USB demod, TX=probably AM (hardware limitation)
Perfect for: Receive SSB, transmit AM on same frequency
"""

import shutil
from pathlib import Path
from datetime import datetime
import hashlib

def patch_enable_usb_mode(input_path, output_path):
    """
    Patch firmware to enable mode 0x04 (USB) transmission

    Original mask: 0x03 (binary: 00000011) - FM and AM only
    New mask:      0x13 (binary: 00010011) - FM, AM, and USB (mode 0x04)

    Bit calculation:
    mode 0x04: 1 << 4 = 0b00010000 = 0x10
    0x10 & 0x13 = 0x10 (non-zero) -> TX ALLOWED
    """

    print("="*80)
    print("TK11 FIRMWARE PATCHER - ENABLE USB MODE TX")
    print("="*80)
    print("\nThis patch enables mode 0x04 (USB) to transmit.")
    print("\nExpected behavior:")
    print("  RX: USB demodulation (already works)")
    print("  TX: Probably AM modulation (hardware limitation)")
    print("\nPerfect for: Receive SSB, reply in AM on same frequency")
    print("="*80)

    # Read firmware
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nInput firmware: {input_path}")
    print(f"Size: {len(data):,} bytes")

    # Patch location (most likely candidate from analysis)
    offset = 0x0000314D

    print(f"\nPatch offset: 0x{offset:08X}")

    original_value = data[offset]
    new_value = 0x13  # Enable FM (bit 0), AM (bit 1), USB (bit 4)

    print(f"Original value: 0x{original_value:02X} (binary: {original_value:08b})")
    print(f"New value:      0x{new_value:02X} (binary: {new_value:08b})")

    if original_value != 0x03:
        print(f"\n[WARNING] Expected 0x03, found 0x{original_value:02X}")
        print("Patch may not work correctly!")
        response = input("\nContinue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return False

    # Apply patch
    data[offset] = new_value

    # Write output
    with open(output_path, 'wb') as f:
        f.write(data)

    # Verify
    with open(output_path, 'rb') as f:
        verify_data = f.read()

    if verify_data[offset] != new_value:
        print("\n[ERROR] Verification failed!")
        return False

    checksum = hashlib.sha256(verify_data).hexdigest()

    print(f"\n[OK] Patch applied successfully!")
    print(f"Output file: {output_path}")
    print(f"SHA256: {checksum[:16]}...")

    return True

def main():
    print("="*80)
    print("TK11 USB MODE TX ENABLER")
    print("="*80)
    print("""
This tool patches firmware to enable USB mode (0x04) transmission.

WHAT THIS DOES:
- Allows K38 USB channel to transmit (no more "DISABLE")
- RX: USB demodulation (receive SSB signals)
- TX: Probably AM modulation (hardware can't do real SSB)

USE CASE:
You want to:
  1. RECEIVE in USB/LSB mode (hear SSB stations)
  2. TRANSMIT in AM mode (reply to them)
  3. Use same frequency for both

This is PERFECT for that!

WARNINGS:
- Can brick radio if incorrect
- Voids warranty
- Test with dummy load first
- Use at your own risk
""")

    response = input("\nDo you understand and accept the risks? (type 'I ACCEPT'): ")

    if response != "I ACCEPT":
        print("\nAborted.")
        return

    input_path = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    output_dir = Path(r"E:\AI\tk11\patched_firmware")

    if not input_path.exists():
        print(f"\n[ERROR] Firmware not found: {input_path}")
        return

    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup
    backup_path = output_dir / f"TK11_ORIGINAL_{timestamp}.bin"
    shutil.copy2(input_path, backup_path)
    print(f"\n[OK] Backup: {backup_path.name}")

    # Create patched firmware
    output_name = f"TK11_PATCHED_USB_TX_ENABLE_{timestamp}.bin"
    output_path = output_dir / output_name

    success = patch_enable_usb_mode(input_path, output_path)

    if success:
        print("\n" + "="*80)
        print("PATCH SUCCESSFUL!")
        print("="*80)
        print(f"""
Patched firmware created: {output_name}

NEXT STEPS:

1. Flash this firmware to your radio
   (See FIRMWARE_FLASH_GUIDE.md for procedure)

2. Use ORIGINAL TK11.dat (no modification needed!)
   - K38 USB channel already exists
   - Mode 0x04 (USB) is already configured

3. Test procedure:
   a. Load original TK11.dat into TK11.exe
   b. Upload to radio
   c. Select K38 USB channel (2.7385 MHz)
   d. Connect 50 ohm dummy load
   e. Press PTT

   Expected: NO "DISABLE" message!

4. Receive test:
   - Tune to USB frequency
   - Listen for SSB stations
   - You should hear them in USB mode

5. Transmit test:
   - Press PTT
   - Monitor on spectrum analyzer
   - Modulation will likely be AM (carrier + 2 sidebands)
   - This is PERFECT for your use case!

WHY THIS WORKS:
- USB stations will hear you (AM contains USB sideband)
- You will hear them (USB demodulation works on RX)
- Compatible with both SSB and AM stations

VERIFICATION:
If you see AM modulation on TX (carrier + 2 sidebands):
  -> SUCCESS! This is exactly what you want!

The radio is doing:
  RX: USB demodulation (SSB capable)
  TX: AM modulation (compatible with SSB receivers)

This is the IDEAL hybrid mode for your use case!
""")
    else:
        print("\n[ERROR] Patch failed!")

    print("="*80)

if __name__ == "__main__":
    main()
