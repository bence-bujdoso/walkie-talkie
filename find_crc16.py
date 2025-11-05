#!/usr/bin/env python3
"""
Find and fix CRC16 in firmware header
Based on TK11.exe mentioning "u16CRC" validation
"""

from pathlib import Path
import struct

def crc16_xmodem(data):
    """CRC16 XMODEM algorithm (common in firmware)"""
    crc = 0
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def crc16_ccitt(data):
    """CRC16 CCITT algorithm"""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def crc16_modbus(data):
    """CRC16 MODBUS algorithm"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def search_crc16_in_header(firmware_path):
    """Search for CRC16 values in firmware header"""

    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print(f"SEARCHING FOR CRC16: {firmware_path.name}")
    print("="*80)

    # Try different data ranges for CRC calculation
    ranges = [
        (0x20, len(data) - 4, "After first 32 bytes to end-4"),
        (0x00, len(data) - 4, "Entire file minus last 4"),
        (0x10, len(data) - 4, "After first 16 bytes to end-4"),
        (0x04, len(data) - 4, "After first 4 bytes to end-4"),
        (0x08, len(data) - 4, "After first 8 bytes to end-4"),
        (0x0C, len(data) - 4, "After first 12 bytes to end-4"),
        (0x100, len(data) - 4, "After first 256 bytes to end-4"),
    ]

    print("\nCalculating CRC16 for different ranges...")

    results = {}

    for start, end, desc in ranges:
        test_data = data[start:end]

        crc_xmodem = crc16_xmodem(test_data)
        crc_ccitt = crc16_ccitt(test_data)
        crc_modbus = crc16_modbus(test_data)

        results[desc] = {
            'xmodem': crc_xmodem,
            'ccitt': crc_ccitt,
            'modbus': crc_modbus,
        }

        print(f"\n{desc}:")
        print(f"  CRC16-XMODEM: 0x{crc_xmodem:04X}")
        print(f"  CRC16-CCITT:  0x{crc_ccitt:04X}")
        print(f"  CRC16-MODBUS: 0x{crc_modbus:04X}")

    # Now search for these values in the first 256 bytes of the file
    print("\n" + "="*80)
    print("SEARCHING FOR CRC16 VALUES IN HEADER (first 256 bytes)")
    print("="*80)

    header = data[:256]

    for i in range(0, len(header) - 1, 2):
        # Read as little-endian 16-bit
        crc_le = struct.unpack('<H', header[i:i+2])[0]
        # Read as big-endian 16-bit
        crc_be = struct.unpack('>H', header[i:i+2])[0]

        # Check if this matches any calculated CRC
        for desc, crcs in results.items():
            for algo, value in crcs.items():
                if crc_le == value:
                    print(f"\n*** MATCH FOUND (LE) at offset 0x{i:04X} ***")
                    print(f"    Value: 0x{crc_le:04X}")
                    print(f"    Algorithm: CRC16-{algo.upper()}")
                    print(f"    Data range: {desc}")
                    return i, value, algo, desc, 'le'

                if crc_be == value:
                    print(f"\n*** MATCH FOUND (BE) at offset 0x{i:04X} ***")
                    print(f"    Value: 0x{crc_be:04X}")
                    print(f"    Algorithm: CRC16-{algo.upper()}")
                    print(f"    Data range: {desc}")
                    return i, value, algo, desc, 'be'

    print("\nNo CRC16 match found in header")
    return None

def compare_original_vs_patched():
    """Compare CRC16 values between original and patched"""

    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin")

    print("\n" + "="*80)
    print("COMPARING ORIGINAL AND PATCHED FIRMWARE")
    print("="*80)

    print("\nORIGINAL FIRMWARE:")
    orig_result = search_crc16_in_header(original)

    print("\n\nPATCHED FIRMWARE:")
    patch_result = search_crc16_in_header(patched)

    return orig_result, patch_result

def show_header_bytes():
    """Show the first 256 bytes of both firmwares side by side"""

    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin")

    with open(original, 'rb') as f:
        orig_data = f.read(256)

    with open(patched, 'rb') as f:
        patch_data = f.read(256)

    print("\n" + "="*80)
    print("HEADER COMPARISON (first 256 bytes)")
    print("="*80)

    print("\nOffset  Original                           Patched")
    print("-" * 80)

    for i in range(0, 256, 16):
        orig_line = orig_data[i:i+16]
        patch_line = patch_data[i:i+16]

        orig_hex = ' '.join(f'{b:02x}' for b in orig_line)
        patch_hex = ' '.join(f'{b:02x}' for b in patch_line)

        match = "=" if orig_line == patch_line else "!= DIFF"

        print(f"0x{i:04X}: {orig_hex:<48} {match}")
        if orig_line != patch_line:
            print(f"       {patch_hex:<48}")

if __name__ == "__main__":
    show_header_bytes()
    compare_original_vs_patched()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
If a CRC16 match was found, the firmware likely uses that for validation.
If not, the TK11.exe might be checking:
  1. A specific version byte/string
  2. A different checksum algorithm
  3. A signature or encrypted header
  4. File size validation

Next step: Examine bytes that differ between original and other working firmware
files to identify version fields.
""")
