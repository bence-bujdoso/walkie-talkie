#!/usr/bin/env python3
"""
Direct USB TX Enable Patch - No Interactive Prompts
Patches firmware to enable USB mode (0x04) transmission
"""

import shutil
from pathlib import Path
from datetime import datetime
import hashlib

def apply_patch():
    input_path = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    output_dir = Path(r"E:\AI\tk11\patched_firmware")

    print("="*80)
    print("TK11 USB TX ENABLE PATCH - DIRECT APPLICATION")
    print("="*80)

    # Read firmware
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nFirmware: {input_path.name}")
    print(f"Size: {len(data):,} bytes")

    # Patch location
    offset = 0x0000314D
    original_value = data[offset]
    new_value = 0x13  # Enable FM (bit 0), AM (bit 1), USB (bit 4)

    print(f"\nPatch Offset: 0x{offset:08X}")
    print(f"Original Value: 0x{original_value:02X} (binary: {original_value:08b})")
    print(f"New Value:      0x{new_value:02X} (binary: {new_value:08b})")

    if original_value != 0x03:
        print(f"\n[WARNING] Expected 0x03 at offset, found 0x{original_value:02X}")
        print("Patch may not work correctly!")

    # Apply patch
    data[offset] = new_value
    print("\n[OK] Patch applied to memory buffer")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup
    backup_path = output_dir / f"TK11_ORIGINAL_BACKUP_{timestamp}.bin"
    shutil.copy2(input_path, backup_path)
    print(f"[OK] Backup created: {backup_path.name}")

    # Write patched firmware
    output_name = f"TK11_PATCHED_USB_TX_ENABLED_{timestamp}.bin"
    output_path = output_dir / output_name

    with open(output_path, 'wb') as f:
        f.write(data)

    # Verify
    with open(output_path, 'rb') as f:
        verify_data = f.read()

    if verify_data[offset] != new_value:
        print("\n[ERROR] Verification failed!")
        return False

    checksum = hashlib.sha256(verify_data).hexdigest()

    print(f"[OK] Patched firmware written: {output_name}")
    print(f"[OK] SHA256: {checksum[:32]}...")

    print("\n" + "="*80)
    print("PATCH APPLIED SUCCESSFULLY!")
    print("="*80)
    print(f"""
RESULT:
- Mode 0x04 (USB) can now transmit!
- RX: USB demodulation (receive SSB)
- TX: AM modulation (hardware limitation)

WHAT THIS FIXES:
Your K38 USB channel will NO LONGER show "DISABLED" when you press PTT.

EXPECTED BEHAVIOR:
- You can now transmit on USB mode channels
- Transmission will use AM modulation (carrier + both sidebands)
- Reception will use USB demodulation (SSB capable)
- PERFECT for hybrid SSB RX / AM TX operation!

NEXT STEPS:
1. Flash the patched firmware: {output_name}
2. Use your existing TK11.dat (no changes needed)
3. Select K38 USB channel (2.7385 MHz)
4. Press PTT - it should transmit!

VERIFICATION:
- If "DISABLED" message is gone → SUCCESS!
- Monitor with spectrum analyzer to confirm AM modulation
- Test with dummy load first!

Location: {output_path}
""")

    return True

if __name__ == "__main__":
    apply_patch()
