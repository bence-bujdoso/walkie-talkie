#!/usr/bin/env python3
"""Analyze TK11.exe to find firmware validation logic"""

from pathlib import Path
import struct

def search_strings(exe_path, search_terms):
    with open(exe_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print("SEARCHING TK11.EXE FOR VALIDATION STRINGS")
    print("="*80)

    for term in search_terms:
        term_bytes = term.encode('ascii', errors='ignore')
        offset = data.find(term_bytes)
        if offset != -1:
            print(f"\nFound '{term}' at offset 0x{offset:08X}")

            # Show context
            start = max(0, offset - 50)
            end = min(len(data), offset + len(term_bytes) + 50)
            context = data[start:end]

            # Try to decode as ASCII
            try:
                decoded = context.decode('ascii', errors='replace')
                print(f"Context: {decoded}")
            except:
                hex_str = ' '.join(f'{b:02x}' for b in context[:50])
                print(f"Context (hex): {hex_str}")

def analyze_firmware_header_structure():
    """Compare original and patched firmware headers in detail"""

    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin")

    print("\n" + "="*80)
    print("DETAILED HEADER COMPARISON")
    print("="*80)

    with open(original, 'rb') as f:
        orig_data = f.read()

    with open(patched, 'rb') as f:
        patch_data = f.read()

    # Check first 1024 bytes in detail
    print("\nFirst 1024 bytes comparison:")

    diffs = []
    for i in range(min(1024, len(orig_data), len(patch_data))):
        if orig_data[i] != patch_data[i]:
            diffs.append(i)

    if diffs:
        print(f"\nDifferences in header: {len(diffs)} bytes")
        for offset in diffs:
            print(f"  0x{offset:08X}: 0x{orig_data[offset]:02X} -> 0x{patch_data[offset]:02X}")
    else:
        print("\nNo differences in first 1024 bytes")

    # Check specific interesting offsets
    print("\n" + "="*80)
    print("CHECKING SPECIFIC HEADER FIELDS")
    print("="*80)

    offsets = [
        (0x00, 4, "Magic/Signature"),
        (0x04, 4, "Header field 1"),
        (0x08, 4, "Header field 2"),
        (0x0C, 4, "Header field 3"),
        (0x10, 4, "Header field 4"),
        (0x14, 4, "Header field 5"),
        (0x18, 4, "Header field 6"),
        (0x1C, 4, "Header field 7"),
    ]

    for offset, size, desc in offsets:
        orig_val = orig_data[offset:offset+size]
        patch_val = patch_data[offset:offset+size]

        orig_int = struct.unpack('<I', orig_val)[0]
        patch_int = struct.unpack('<I', patch_val)[0]

        match = "MATCH" if orig_val == patch_val else "DIFF"

        print(f"\n{desc} (0x{offset:02X}):")
        print(f"  Original: 0x{orig_int:08X}  [{match}]")
        print(f"  Patched:  0x{patch_int:08X}")

        if orig_val != patch_val:
            print(f"  Difference: {orig_val.hex()} -> {patch_val.hex()}")

def check_multiple_checksums():
    """Check if there are multiple checksums in the firmware"""

    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin")

    print("\n" + "="*80)
    print("CHECKING FOR MULTIPLE CHECKSUM FIELDS")
    print("="*80)

    with open(original, 'rb') as f:
        orig_data = f.read()

    with open(patched, 'rb') as f:
        patch_data = f.read()

    # Check various ranges for checksums
    ranges = [
        (0, 0x100, "First 256 bytes"),
        (0x100, 0x1000, "First 4KB minus header"),
        (0, len(orig_data) - 4, "Entire file minus last 4"),
        (0, len(orig_data) - 8, "Entire file minus last 8"),
        (0x100, len(orig_data) - 4, "After header to end minus 4"),
    ]

    for start, end, desc in ranges:
        orig_sum = sum(orig_data[start:end]) & 0xFFFFFFFF
        patch_sum = sum(patch_data[start:end]) & 0xFFFFFFFF

        print(f"\n{desc}:")
        print(f"  Original checksum: 0x{orig_sum:08X}")
        print(f"  Patched checksum:  0x{patch_sum:08X}")
        print(f"  Difference:        0x{abs(patch_sum - orig_sum):08X}")

if __name__ == "__main__":
    exe_path = Path(r"E:\AI\tk11\TK11.exe")

    if exe_path.exists():
        search_terms = [
            "File version is Wrong",
            "version",
            "Version",
            "VERSION",
            "Wrong",
            "wrong",
            "v5.00.09",
            "5.00.09",
            "checksum",
            "Checksum",
            "CRC",
            "signature",
        ]

        search_strings(exe_path, search_terms)

    analyze_firmware_header_structure()
    check_multiple_checksums()
