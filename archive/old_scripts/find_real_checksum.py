#!/usr/bin/env python3
"""
Find the REAL checksum location and algorithm
Since the last 4 bytes aren't it, the checksum must be elsewhere
"""

from pathlib import Path
import struct
import binascii

def calculate_checksums_for_range(data, start, end, name):
    """Calculate various checksums for a data range"""

    subset = data[start:end]

    results = {
        'range': name,
        'start': start,
        'end': end,
        'size': len(subset),
        'sum32_le': sum(subset) & 0xFFFFFFFF,
        'xor': sum(subset) & 0xFF,
        'crc32': binascii.crc32(subset) & 0xFFFFFFFF,
    }

    return results

def search_for_checksum_field(firmware_path):
    """Search for where a checksum might be stored"""

    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print(f"ANALYZING: {firmware_path.name}")
    print("="*80)

    # Define various data ranges to checksum
    ranges = [
        (0x00, len(data), "Entire file"),
        (0x04, len(data), "Skip first 4 bytes"),
        (0x08, len(data), "Skip first 8 bytes"),
        (0x0C, len(data), "Skip first 12 bytes"),
        (0x10, len(data), "Skip first 16 bytes"),
        (0x20, len(data), "Skip first 32 bytes"),
        (0x100, len(data), "Skip first 256 bytes"),
        (0x00, len(data) - 4, "Skip last 4 bytes"),
        (0x00, len(data) - 8, "Skip last 8 bytes"),
        (0x04, len(data) - 4, "Skip first 4 and last 4"),
        (0x08, len(data) - 8, "Skip first 8 and last 8"),
        (0x0C, len(data) - 4, "Skip first 12 and last 4"),
    ]

    checksums = []

    for start, end, name in ranges:
        result = calculate_checksums_for_range(data, start, end, name)
        checksums.append(result)

    # Now search for these checksum values in the first 256 bytes
    print("\n[SEARCHING FOR CHECKSUM VALUES IN HEADER]")
    print("-" * 80)

    header = data[:256]

    found_any = False

    for i in range(0, len(header) - 3):
        # Try reading as 32-bit LE
        value_le = struct.unpack('<I', header[i:i+4])[0]

        # Check against all calculated checksums
        for cs in checksums:
            if value_le == cs['sum32_le']:
                print(f"\n*** MATCH: SUM32 ***")
                print(f"  Offset: 0x{i:04X}")
                print(f"  Value: 0x{value_le:08X}")
                print(f"  Range: {cs['range']}")
                found_any = True

            if value_le == cs['crc32']:
                print(f"\n*** MATCH: CRC32 ***")
                print(f"  Offset: 0x{i:04X}")
                print(f"  Value: 0x{value_le:08X}")
                print(f"  Range: {cs['range']}")
                found_any = True

    if not found_any:
        print("\nNo checksum match found in first 256 bytes")

        # Try looking in other areas
        print("\n[CHECKING OTHER POTENTIAL LOCATIONS]")
        print("-" * 80)

        locations = [
            (0x100, "Offset 0x100"),
            (0x200, "Offset 0x200"),
            (0x400, "Offset 0x400"),
            (len(data) - 256, "Last 256 bytes start"),
        ]

        for loc, desc in locations:
            if loc + 4 <= len(data):
                value = struct.unpack('<I', data[loc:loc+4])[0]

                for cs in checksums:
                    if value == cs['sum32_le']:
                        print(f"\n*** MATCH: SUM32 at {desc} ***")
                        print(f"  Offset: 0x{loc:04X}")
                        print(f"  Value: 0x{value:08X}")
                        print(f"  Range: {cs['range']}")
                        found_any = True

                    if value == cs['crc32']:
                        print(f"\n*** MATCH: CRC32 at {desc} ***")
                        print(f"  Offset: 0x{loc:04X}")
                        print(f"  Value: 0x{value:08X}")
                        print(f"  Range: {cs['range']}")
                        found_any = True

    return checksums

def main():
    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")

    print("\n" + "="*80)
    print("ORIGINAL FIRMWARE ANALYSIS")
    print("="*80)
    search_for_checksum_field(original)

    print("\n\n" + "="*80)
    print("HYPOTHESIS: Maybe there's NO checksum to fix!")
    print("="*80)
    print("""
The "File version is Wrong!" error might mean:

1. TK11.exe is checking the firmware is ENCRYPTED properly
   - Our patch broke the encryption
   - Need to re-encrypt after patching

2. TK11.exe checks SPECIFIC BYTES for a version marker
   - Not a checksum, but actual version bytes
   - Need to find what bytes indicate "v5.00.09"

3. TK11.exe requires EXACT FILE SIZE
   - Check if file size changed

4. TK11.exe uses SIGNED firmware
   - Firmware has a cryptographic signature
   - Modifying any byte breaks the signature
   - Might be impossible to patch without private key

5. The error message is MISLEADING
   - "File version is Wrong!" might not mean file validation
   - Could mean: firmware version incompatible with TK11.exe version
   - Could mean: wrong RADIO model

Let me check a few more things...
""")

if __name__ == "__main__":
    main()
