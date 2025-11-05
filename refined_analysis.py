#!/usr/bin/env python3
"""
Refined TK11.dat analysis with correct frequency detection
"""

import struct
from pathlib import Path

RECORD_SIZE = 64

def hex_view(data, width=16):
    """Pretty hex view"""
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"{i:04x}  {hex_str:<48}  |{ascii_str}|")
    return '\n'.join(lines)

def main():
    file_path = Path(r"E:\AI\tk11\TK11.dat")

    with open(file_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print("REFINED ANALYSIS - First few records in detail")
    print("="*80)

    # Look at first 10 records
    for rec_num in range(10):
        offset = rec_num * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        print(f"\n{'='*80}")
        print(f"Record {rec_num} (Offset: {offset:#010x}, {offset})")
        print(f"{'='*80}")
        print(hex_view(record))

        # Try to parse
        freq_raw = struct.unpack('<I', record[0:4])[0]
        print(f"\nParsed fields:")
        print(f"  Bytes 0-3 (freq?): {freq_raw:#010x} = {freq_raw} Hz = {freq_raw/1e6:.4f} MHz")

        if record[0:4] != b'\xff\xff\xff\xff' and freq_raw > 0:
            # Check bytes 4-7
            tx_raw = struct.unpack('<I', record[4:8])[0]
            print(f"  Bytes 4-7 (tx?):   {tx_raw:#010x} = {tx_raw} Hz = {tx_raw/1e6:.4f} MHz")

            # CTCSS/DCS
            rx_tone = struct.unpack('<H', record[8:10])[0]
            tx_tone = struct.unpack('<H', record[10:12])[0]
            print(f"  Bytes 8-9 (RX tone): {rx_tone:#06x}")
            print(f"  Bytes 10-11 (TX tone): {tx_tone:#06x}")

            # Flag bytes
            print(f"\n  Flag bytes:")
            for i in range(12, 24):
                print(f"    Byte {i:2d}: {record[i]:#04x} ({record[i]:3d}) {bin(record[i])}")

            # Channel name
            name = record[24:40].decode('ascii', errors='ignore').rstrip('\x00')
            print(f"\n  Bytes 24-39 (Name): '{name}'")

            # Remaining
            print(f"\n  Bytes 40-63:")
            for i in range(40, 64, 4):
                vals = ' '.join(f'{record[j]:#04x}' for j in range(i, min(i+4, 64)))
                print(f"    Bytes {i:2d}-{min(i+3, 63):2d}: {vals}")

    # Look specifically at channels that were modified
    print("\n" + "="*80)
    print("EXAMINING TX-LOCKED CHANNELS")
    print("="*80)

    locked_channels = [
        1044, 1045, 1046, 1047, 1048, 1049, 1088,
        1408, 1410, 1412, 1414, 1416
    ]

    for ch_num in locked_channels[:5]:  # First 5
        offset = ch_num * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        print(f"\n--- Channel {ch_num} (was TX-locked) ---")
        print(hex_view(record))

        freq = struct.unpack('<I', record[0:4])[0]
        print(f"\nFrequency: {freq/1e6:.4f} MHz")
        print(f"Byte 22 (TX permit?): {record[22]:#04x} (binary: {bin(record[22])})")

        name = record[24:40].decode('ascii', errors='ignore').rstrip('\x00')
        if name:
            print(f"Channel name: '{name}'")

    # Check the file header/structure
    print("\n" + "="*80)
    print("FILE HEADER ANALYSIS")
    print("="*80)

    # First 256 bytes might be header
    header = data[0:256]
    print("First 256 bytes:")
    print(hex_view(header))

    # Look for structure markers
    print("\n" + "="*80)
    print("SEARCHING FOR STRUCTURE PATTERNS")
    print("="*80)

    # Find all non-empty, non-0xFF records
    active_offsets = []
    for i in range(len(data) // RECORD_SIZE):
        offset = i * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        # Skip all 0x00 or all 0xFF
        if record == b'\x00' * RECORD_SIZE or record == b'\xff' * RECORD_SIZE:
            continue

        # Check if has some data
        non_zero = sum(1 for b in record if b != 0x00 and b != 0xff)
        if non_zero > 4:
            active_offsets.append((i, offset))

    print(f"\nFound {len(active_offsets)} potentially active records")
    print("\nFirst 20 active record positions:")
    for idx, (rec_num, offset) in enumerate(active_offsets[:20]):
        record = data[offset:offset+RECORD_SIZE]
        freq = struct.unpack('<I', record[0:4])[0]
        name = record[24:40].decode('ascii', errors='ignore').rstrip('\x00')
        byte_22 = record[22]

        print(f"  Rec {rec_num:4d} @ {offset:#010x}: freq={freq/1e6:8.4f}MHz  byte22={byte_22:#04x}  name='{name}'")

if __name__ == "__main__":
    main()
