#!/usr/bin/env python3
"""
TK11 Patched Firmware Generator
Generates 8 firmware variants with USB TX unlock
"""

import struct
import os
import sys
from pathlib import Path

class TK11FirmwarePatcher:
    def __init__(self, original_firmware_path):
        """Initialize with original firmware file"""
        if not os.path.exists(original_firmware_path):
            raise FileNotFoundError(f"Original firmware not found: {original_firmware_path}")

        self.original_path = original_firmware_path

        # Read original firmware
        with open(original_firmware_path, 'rb') as f:
            self.firmware_data = bytearray(f.read())

        print(f"[+] Loaded firmware: {len(self.firmware_data)} bytes")
        print(f"[+] Original file: {original_firmware_path}")

    def crc16_xmodem(self, data):
        """CRC16-XMODEM (polynomial 0x1021)"""
        crc = 0x0000
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
                crc &= 0xFFFF
        return crc

    def crc16_ibm(self, data):
        """CRC16-IBM (polynomial 0x8005)"""
        crc = 0x0000
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0x8005
                else:
                    crc = crc >> 1
        return crc

    def apply_tx_unlock(self, data):
        """Apply USB TX unlock at offset 0x314D"""
        TX_MASK_OFFSET = 0x314D

        if TX_MASK_OFFSET >= len(data):
            print(f"[!] Warning: TX mask offset 0x{TX_MASK_OFFSET:04X} is beyond firmware size")
            return False

        original_value = data[TX_MASK_OFFSET]
        print(f"[*] Original TX mask at 0x{TX_MASK_OFFSET:04X}: 0x{original_value:02X}")

        # Enable USB TX (set bit 4)
        data[TX_MASK_OFFSET] = 0x13

        new_value = data[TX_MASK_OFFSET]
        print(f"[+] Patched TX mask to: 0x{new_value:02X}")
        print(f"    Binary: {bin(original_value)} -> {bin(new_value)}")
        print(f"    Effect: USB (0x04) mode TX now ENABLED")

        return True

    def create_variant_1_simple(self, output_dir):
        """Variant 1: Simple patch with CRC16-XMODEM at end"""
        print("\n[*] Creating Variant 1: Simple CRC16-XMODEM...")

        data = self.firmware_data.copy()
        self.apply_tx_unlock(data)

        # Calculate CRC16-XMODEM for entire data except last 2 bytes
        crc_data = bytes(data[:-2])
        crc = self.crc16_xmodem(crc_data)

        # Write CRC16 at end (little-endian)
        struct.pack_into('<H', data, len(data) - 2, crc)

        output_path = output_dir / "TK11_PATCHED_v1_simple_crc16xmodem.bin"
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"[+] Created: {output_path.name}")
        print(f"    Size: {len(data)} bytes")
        print(f"    CRC16-XMODEM: 0x{crc:04X} at offset 0x{len(data)-2:X}")
        return output_path

    def create_variant_2_ibm(self, output_dir):
        """Variant 2: Patch with CRC16-IBM at end"""
        print("\n[*] Creating Variant 2: CRC16-IBM...")

        data = self.firmware_data.copy()
        self.apply_tx_unlock(data)

        # Calculate CRC16-IBM
        crc_data = bytes(data[:-2])
        crc = self.crc16_ibm(crc_data)

        # Write CRC16 at end (little-endian)
        struct.pack_into('<H', data, len(data) - 2, crc)

        output_path = output_dir / "TK11_PATCHED_v2_crc16ibm.bin"
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"[+] Created: {output_path.name}")
        print(f"    Size: {len(data)} bytes")
        print(f"    CRC16-IBM: 0x{crc:04X} at offset 0x{len(data)-2:X}")
        return output_path

    def create_variant_3_preserve_original(self, output_dir):
        """Variant 3: Preserve original structure, minimal change"""
        print("\n[*] Creating Variant 3: Minimal change (preserve all)...")

        data = self.firmware_data.copy()

        # ONLY change TX mask, nothing else
        self.apply_tx_unlock(data)

        output_path = output_dir / "TK11_PATCHED_v3_minimal.bin"
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"[+] Created: {output_path.name}")
        print(f"    Size: {len(data)} bytes")
        print(f"    Only 1 byte changed at 0x314D")
        return output_path

    def create_variant_4_multiple_crc_positions(self, output_dir):
        """Variant 4: Try CRC at multiple potential positions"""
        print("\n[*] Creating Variant 4: Multiple CRC positions...")

        variants = []

        # Potential CRC positions based on code analysis
        crc_positions = [
            (0x000C, "header_0x0C"),
            (0x0010, "header_0x10"),
            (0x001C, "header_0x1C"),
            (0x0020, "header_0x20"),
            (len(self.firmware_data) - 2, "end_of_file"),
        ]

        for offset, name in crc_positions:
            data = self.firmware_data.copy()
            self.apply_tx_unlock(data)

            # Calculate CRC16-XMODEM for data up to CRC position
            if offset < len(data) - 2:
                # CRC of data before and after CRC field
                crc_data = bytes(data[:offset]) + bytes(data[offset+2:len(data)])
            else:
                # CRC of all data except last 2 bytes
                crc_data = bytes(data[:offset])

            crc = self.crc16_xmodem(crc_data)

            # Write CRC16 at position
            struct.pack_into('<H', data, offset, crc)

            output_path = output_dir / f"TK11_PATCHED_v4_{name}.bin"
            with open(output_path, 'wb') as f:
                f.write(data)

            print(f"[+] Created: {output_path.name}")
            print(f"    Size: {len(data)} bytes")
            print(f"    CRC16-XMODEM: 0x{crc:04X} at offset 0x{offset:X}")
            variants.append(output_path)

        return variants

    def create_all_variants(self, output_dir):
        """Create all firmware variants"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("TK11 PATCHED FIRMWARE GENERATOR")
        print("="*80)
        print(f"\n[+] Output directory: {output_dir.absolute()}")

        variants = []
        variants.append(self.create_variant_1_simple(output_dir))
        variants.append(self.create_variant_2_ibm(output_dir))
        variants.append(self.create_variant_3_preserve_original(output_dir))
        variants.extend(self.create_variant_4_multiple_crc_positions(output_dir))

        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"\n[+] Created {len(variants)} firmware variants:")
        for i, variant in enumerate(variants, 1):
            size = os.path.getsize(variant)
            print(f"    {i}. {variant.name:45s} ({size:,} bytes)")

        print(f"\n[+] All files saved to: {output_dir.absolute()}")

        print("\n[*] TESTING RECOMMENDATION:")
        print("    1. Test v3_minimal first (most conservative)")
        print("    2. Then try v1_simple_crc16xmodem")
        print("    3. Then try v4_* variants")
        print("    4. Finally try v2_crc16ibm")

        return variants

def main():
    """Main entry point"""
    print("TK11 Patched Firmware Generator")
    print("================================\n")

    # Check for original firmware
    script_dir = Path(__file__).parent
    bin_dir = script_dir.parent
    original_dir = bin_dir / "original"
    output_dir = bin_dir / "patched_firmware"

    # Look for firmware file
    firmware_files = list(original_dir.glob("TK11*.bin"))

    if not firmware_files:
        print("[!] ERROR: No firmware file found!")
        print(f"[!] Please place the original firmware in: {original_dir.absolute()}")
        print("[!] Expected filename: TK11_v5.00.09_ENG.bin or similar")
        print("")
        print("To use this script:")
        print("1. Download TK11_v5.00.09_ENG.bin from https://itistesla.com/ai/TK11_v5.00.09_ENG.bin")
        print(f"2. Place it in: {original_dir.absolute()}")
        print("3. Run this script again")
        return 1

    # Use the first firmware file found
    original_firmware = firmware_files[0]
    print(f"[+] Found firmware: {original_firmware.name}")

    try:
        patcher = TK11FirmwarePatcher(str(original_firmware))
        variants = patcher.create_all_variants(output_dir)

        print("\n[✓] Done! All patched firmware variants created successfully!")
        print(f"[✓] Output: {output_dir.absolute()}")

        return 0

    except Exception as e:
        print(f"\n[!] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
