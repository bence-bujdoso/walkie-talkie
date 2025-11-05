#!/usr/bin/env python3
"""
TK11 Perfect Firmware Patcher
Creates bootloader-compatible patched firmware with USB TX unlock
"""

import struct
import os
from pathlib import Path

class TK11FirmwarePatcher:
    def __init__(self, original_firmware_path):
        self.original_path = original_firmware_path
        self.output_dir = Path("patched_firmware_final")
        self.output_dir.mkdir(exist_ok=True)

        # Read original firmware
        with open(original_firmware_path, 'rb') as f:
            self.firmware_data = bytearray(f.read())

        print(f"[+] Loaded firmware: {len(self.firmware_data)} bytes")

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

    def apply_tx_unlock(self):
        """Apply USB TX unlock at offset 0x314D"""
        TX_MASK_OFFSET = 0x314D

        original_value = self.firmware_data[TX_MASK_OFFSET]
        print(f"[*] Original TX mask at 0x{TX_MASK_OFFSET:04X}: 0x{original_value:02X}")

        # Enable USB TX (set bit 4)
        self.firmware_data[TX_MASK_OFFSET] = 0x13

        new_value = self.firmware_data[TX_MASK_OFFSET]
        print(f"[+] Patched TX mask to: 0x{new_value:02X}")
        print(f"    Binary: {bin(original_value)} -> {bin(new_value)}")
        print(f"    Effect: USB (0x04) mode TX now ENABLED")

    def create_variant_1_simple(self):
        """Variant 1: Simple patch with CRC16-XMODEM at end"""
        print("\n[*] Creating Variant 1: Simple CRC16-XMODEM...")

        data = self.firmware_data.copy()

        # Apply TX unlock
        data[0x314D] = 0x13

        # Calculate CRC16-XMODEM for entire data except last 2 bytes
        crc_data = bytes(data[:-2])
        crc = self.crc16_xmodem(crc_data)

        # Write CRC16 at end (little-endian)
        struct.pack_into('<H', data, len(data) - 2, crc)

        output_path = self.output_dir / "TK11_PATCHED_v1_simple_crc16xmodem.bin"
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"[+] Created: {output_path}")
        print(f"    CRC16-XMODEM: 0x{crc:04X} at offset 0x{len(data)-2:X}")
        return output_path

    def create_variant_2_ibm(self):
        """Variant 2: Patch with CRC16-IBM at end"""
        print("\n[*] Creating Variant 2: CRC16-IBM...")

        data = self.firmware_data.copy()

        # Apply TX unlock
        data[0x314D] = 0x13

        # Calculate CRC16-IBM
        crc_data = bytes(data[:-2])
        crc = self.crc16_ibm(crc_data)

        # Write CRC16 at end (little-endian)
        struct.pack_into('<H', data, len(data) - 2, crc)

        output_path = self.output_dir / "TK11_PATCHED_v2_crc16ibm.bin"
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"[+] Created: {output_path}")
        print(f"    CRC16-IBM: 0x{crc:04X} at offset 0x{len(data)-2:X}")
        return output_path

    def create_variant_3_preserve_original(self):
        """Variant 3: Preserve original structure, minimal change"""
        print("\n[*] Creating Variant 3: Minimal change (preserve all)...")

        data = self.firmware_data.copy()

        # ONLY change TX mask, nothing else
        data[0x314D] = 0x13

        output_path = self.output_dir / "TK11_PATCHED_v3_minimal.bin"
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"[+] Created: {output_path}")
        print(f"    Only 1 byte changed at 0x314D")
        return output_path

    def create_variant_4_multiple_crc_positions(self):
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

            # Apply TX unlock
            data[0x314D] = 0x13

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

            output_path = self.output_dir / f"TK11_PATCHED_v4_{name}.bin"
            with open(output_path, 'wb') as f:
                f.write(data)

            print(f"[+] Created: {output_path}")
            print(f"    CRC16-XMODEM: 0x{crc:04X} at offset 0x{offset:X}")
            variants.append(output_path)

        return variants

    def create_all_variants(self):
        """Create all firmware variants"""
        print("="*80)
        print("TK11 PERFECT FIRMWARE PATCHER")
        print("="*80)

        self.apply_tx_unlock()

        variants = []
        variants.append(self.create_variant_1_simple())
        variants.append(self.create_variant_2_ibm())
        variants.append(self.create_variant_3_preserve_original())
        variants.extend(self.create_variant_4_multiple_crc_positions())

        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"\n[+] Created {len(variants)} firmware variants:")
        for i, variant in enumerate(variants, 1):
            print(f"    {i}. {variant.name}")

        print(f"\n[+] All files saved to: {self.output_dir.absolute()}")

        print("\n[*] TESTING RECOMMENDATION:")
        print("    1. Test v3_minimal first (most conservative)")
        print("    2. Then try v1_simple_crc16xmodem")
        print("    3. Then try v4_* variants")
        print("    4. Finally try v2_crc16ibm")

        return variants

def main():
    original_firmware = "TK11_v5.00.09_ENG.bin"

    if not os.path.exists(original_firmware):
        print(f"ERROR: {original_firmware} not found!")
        print("Please ensure the original firmware is in the current directory.")
        return

    patcher = TK11FirmwarePatcher(original_firmware)
    variants = patcher.create_all_variants()

    print("\n[+] Done! Ready to test with patched TK11.exe")

if __name__ == "__main__":
    main()
