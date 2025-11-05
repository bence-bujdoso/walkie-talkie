#!/usr/bin/env python3
"""Analyze firmware version and validation structures"""

from pathlib import Path
import struct

def analyze_firmware_header(firmware_path):
    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print("TK11 FIRMWARE VERSION ANALYSIS")
    print("="*80)
    print(f"\nFirmware: {firmware_path.name}")
    print(f"Size: {len(data):,} bytes (0x{len(data):X})")

    # Check first 256 bytes (typical header area)
    print("\n" + "="*80)
    print("FIRST 256 BYTES (HEADER AREA)")
    print("="*80)

    header = data[:256]

    # Hex dump
    for i in range(0, 256, 16):
        line = header[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in line)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
        print(f"{i:08X}: {hex_str:<48} {ascii_str}")

    # Search for version strings
    print("\n" + "="*80)
    print("SEARCHING FOR VERSION STRINGS")
    print("="*80)

    version_patterns = [
        b'v5.00.09',
        b'5.00.09',
        b'V5.00.09',
        b'TK11',
        b'version',
        b'VERSION'
    ]

    for pattern in version_patterns:
        offset = data.find(pattern)
        if offset != -1:
            # Show context
            start = max(0, offset - 32)
            end = min(len(data), offset + len(pattern) + 32)
            context = data[start:end]

            print(f"\nFound '{pattern.decode('ascii', errors='ignore')}' at offset 0x{offset:08X}")
            print("Context:")

            for i in range(0, len(context), 16):
                line = context[i:i+16]
                hex_str = ' '.join(f'{b:02x}' for b in line)
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)

                addr = start + i
                marker = ""
                if start + i <= offset < start + i + 16:
                    marker = " <-- HERE"

                print(f"  {addr:08X}: {hex_str:<48} {ascii_str}{marker}")

    # Check for checksum/CRC areas
    print("\n" + "="*80)
    print("POTENTIAL CHECKSUM/CRC LOCATIONS")
    print("="*80)

    # Common checksum locations
    locations = [
        (0x00, "Start of file"),
        (0x10, "Offset +16"),
        (0x20, "Offset +32"),
        (0x100, "Offset +256"),
        (len(data) - 4, "Last 4 bytes"),
        (len(data) - 8, "Last 8 bytes"),
        (len(data) - 16, "Last 16 bytes"),
    ]

    for offset, desc in locations:
        if offset >= 0 and offset + 4 <= len(data):
            value32 = struct.unpack('<I', data[offset:offset+4])[0]
            value32_be = struct.unpack('>I', data[offset:offset+4])[0]
            print(f"\n{desc} (0x{offset:08X}):")
            print(f"  Little-endian: 0x{value32:08X} ({value32})")
            print(f"  Big-endian:    0x{value32_be:08X} ({value32_be})")

            # Show bytes
            bytes_at = data[offset:offset+16]
            hex_str = ' '.join(f'{b:02x}' for b in bytes_at)
            print(f"  Raw bytes: {hex_str}")

    # Calculate actual checksums
    print("\n" + "="*80)
    print("CALCULATED CHECKSUMS")
    print("="*80)

    # Simple sum
    checksum_sum = sum(data) & 0xFFFFFFFF
    print(f"\nSimple sum (32-bit): 0x{checksum_sum:08X}")

    # Sum of all bytes except last 4
    if len(data) > 4:
        checksum_sum_minus_last = sum(data[:-4]) & 0xFFFFFFFF
        print(f"Sum without last 4 bytes: 0x{checksum_sum_minus_last:08X}")

    # XOR checksum
    checksum_xor = 0
    for b in data:
        checksum_xor ^= b
    print(f"XOR checksum: 0x{checksum_xor:02X}")

    return data

def compare_original_vs_patched():
    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin")

    print("\n" + "="*80)
    print("COMPARING ORIGINAL VS PATCHED")
    print("="*80)

    with open(original, 'rb') as f:
        orig_data = f.read()

    with open(patched, 'rb') as f:
        patch_data = f.read()

    # Find differences
    differences = []
    for i in range(min(len(orig_data), len(patch_data))):
        if orig_data[i] != patch_data[i]:
            differences.append(i)

    print(f"\nTotal differences: {len(differences)}")
    print("\nDifferences found at:")

    for offset in differences:
        print(f"  0x{offset:08X}: 0x{orig_data[offset]:02X} -> 0x{patch_data[offset]:02X}")

if __name__ == "__main__":
    print("Analyzing ORIGINAL firmware...\n")
    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    analyze_firmware_header(original)

    print("\n" + "="*80)
    print("\nAnalyzing PATCHED firmware...\n")
    patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin")
    analyze_firmware_header(patched)

    compare_original_vs_patched()
