#!/usr/bin/env python3
"""
Convert USB channels to AM mode for TK11
This allows both receive and transmit to work properly.

Usage: python3 convert_usb_to_am.py TK11_am.dat TK11_am_mode.dat
"""

import sys
import struct

def convert_usb_to_am(input_file, output_file):
    """Convert all USB (0x02) channels to AM (0x01)"""

    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    print(f"File size: {len(data)} bytes")
    print(f"Records: {len(data) // 64}")
    print()

    modified_count = 0

    # Process each 64-byte record
    for i in range(len(data) // 64):
        offset = i * 64
        record = data[offset:offset + 64]

        # Parse channel info
        freq = struct.unpack('<I', record[0:4])[0]
        mode_byte = record[16]
        name = record[24:32].decode('ascii', errors='ignore').rstrip('\x00')

        # Skip empty channels
        if freq == 0xFFFFFFFF or mode_byte == 0xFF:
            continue

        # Convert USB to AM
        if mode_byte == 0x02:  # USB
            data[offset + 16] = 0x01  # Change to AM
            modified_count += 1
            print(f"Ch {i:3d}: {freq/1000000:8.4f} MHz - USB → AM - \"{name}\"")

    print()
    print(f"Modified {modified_count} channels from USB to AM")

    # Write output
    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"Saved: {output_file}")
    print()
    print("Next steps:")
    print("  1. Open TK11.exe")
    print("  2. Load the new .dat file")
    print("  3. Upload to radio")
    print("  4. Test both RX and TX on AM mode!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 convert_usb_to_am.py <input.dat> <output.dat>")
        print("Example: python3 convert_usb_to_am.py TK11_am.dat TK11_am_mode.dat")
        sys.exit(1)

    convert_usb_to_am(sys.argv[1], sys.argv[2])
