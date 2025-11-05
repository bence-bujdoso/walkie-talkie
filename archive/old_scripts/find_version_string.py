#!/usr/bin/env python3
"""
Find version strings in firmware
"""

import re
from pathlib import Path

def find_printable_strings(data, min_length=4):
    """Extract printable ASCII strings from binary data"""
    strings = []
    current = []

    for byte in data:
        if 32 <= byte < 127:  # Printable ASCII
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                strings.append(''.join(current))
            current = []

    if len(current) >= min_length:
        strings.append(''.join(current))

    return strings

def main():
    firmware_path = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")

    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print("SEARCHING FOR VERSION STRINGS IN FIRMWARE")
    print("="*80)

    strings = find_printable_strings(data, min_length=4)

    # Filter for version-related strings
    version_patterns = [
        r'v?\d+\.\d+',  # v5.00 or 5.00
        r'version',
        r'TK11',
        r'V\d+',
        r'REV',
        r'firmware',
    ]

    print("\nVersion-related strings found:")
    print("-" * 80)

    found_any = False
    for s in strings:
        for pattern in version_patterns:
            if re.search(pattern, s, re.IGNORECASE):
                # Find offset of this string in firmware
                offset = data.find(s.encode('ascii'))
                print(f"  0x{offset:08X}: {s}")
                found_any = True
                break

    if not found_any:
        print("  No version strings found")

    # Also look for the version number directly
    print("\n" + "="*80)
    print("SEARCHING FOR VERSION BYTES (5.00.09)")
    print("="*80)

    # Version might be stored as BCD or binary
    # 5.00.09 might be:
    # - ASCII: "5.00.09"
    # - BCD: 0x05, 0x00, 0x09
    # - Binary: 5, 0, 9

    print("\nSearching for ASCII '5.00.09':")
    search_str = b"5.00.09"
    offset = data.find(search_str)
    if offset != -1:
        print(f"  Found at 0x{offset:08X}")
    else:
        print("  Not found")

    print("\nSearching for ASCII 'v5.00.09':")
    search_str = b"v5.00.09"
    offset = data.find(search_str)
    if offset != -1:
        print(f"  Found at 0x{offset:08X}")
    else:
        print("  Not found")

    # Search for BCD version
    print("\nSearching for BCD pattern 05 00 09:")
    pattern = bytes([0x05, 0x00, 0x09])
    offset = 0
    count = 0
    while True:
        offset = data.find(pattern, offset)
        if offset == -1:
            break
        print(f"  Found at 0x{offset:08X}: {data[offset:offset+10].hex(' ')}")
        offset += 1
        count += 1
        if count >= 10:
            break

    if count == 0:
        print("  Not found")

    # Look at header more carefully
    print("\n" + "="*80)
    print("FIRST 512 BYTES (potential header/metadata area)")
    print("="*80)

    for i in range(0, 512, 16):
        line = data[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in line)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
        print(f"  {i:04X}: {hex_str:<48} {ascii_str}")

if __name__ == "__main__":
    main()
