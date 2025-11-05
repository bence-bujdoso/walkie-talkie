#!/usr/bin/env python3
"""
TK11.dat Binary File Analyzer
Reverse engineering channel storage format and TX locking mechanisms
"""

import struct
import sys
from pathlib import Path

def hex_dump(data, offset=0, length=512):
    """Display hex dump with annotations"""
    print(f"\n{'='*80}")
    print(f"HEX DUMP - Offset: {offset:#010x}, Length: {length} bytes")
    print(f"{'='*80}")

    for i in range(0, min(length, len(data)), 16):
        # Hex values
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        # ASCII representation
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"{offset+i:08x}  {hex_str:<48}  |{ascii_str}|")

def find_strings(data, min_length=4):
    """Extract printable strings from binary data"""
    strings = []
    current = bytearray()

    for byte in data:
        if 32 <= byte < 127:  # Printable ASCII
            current.append(byte)
        else:
            if len(current) >= min_length:
                strings.append(current.decode('ascii'))
            current = bytearray()

    if len(current) >= min_length:
        strings.append(current.decode('ascii'))

    return strings

def analyze_patterns(data, chunk_size=64):
    """Look for repeating patterns that might indicate channel records"""
    print(f"\n{'='*80}")
    print("PATTERN ANALYSIS - Looking for repeating structures")
    print(f"{'='*80}")

    # Try different record sizes
    for record_size in [32, 40, 48, 56, 64, 80, 96, 128, 256]:
        if len(data) % record_size == 0 or len(data) // record_size > 10:
            num_records = len(data) // record_size
            print(f"\nTesting record size: {record_size} bytes -> {num_records} potential records")

            # Check first few records
            if num_records > 1:
                record1 = data[0:record_size]
                record2 = data[record_size:record_size*2]

                # Compare bytes to find differences
                diffs = sum(1 for i in range(record_size) if record1[i] != record2[i])
                similarity = (record_size - diffs) / record_size * 100
                print(f"  Similarity between record 1 and 2: {similarity:.1f}%")

                if similarity > 30:  # Similar structure
                    print(f"  -> POSSIBLE MATCH: Record size might be {record_size} bytes")

def search_keywords(data):
    """Search for TX/lock related keywords"""
    print(f"\n{'='*80}")
    print("KEYWORD SEARCH - TX/Lock indicators")
    print(f"{'='*80}")

    keywords = [
        b'lock', b'LOCK', b'Lock',
        b'TX', b'tx', b'Tx',
        b'transmit', b'TRANSMIT',
        b'enable', b'ENABLE', b'Enable',
        b'disable', b'DISABLE', b'Disable',
        b'freq', b'FREQ', b'Freq',
        b'channel', b'CHANNEL', b'Channel',
        b'mode', b'MODE', b'Mode'
    ]

    for keyword in keywords:
        positions = []
        start = 0
        while True:
            pos = data.find(keyword, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        if positions:
            print(f"\nFound '{keyword.decode()}' at {len(positions)} position(s):")
            for pos in positions[:10]:  # Show first 10
                context = data[max(0, pos-16):pos+len(keyword)+16]
                print(f"  Offset {pos:#010x}: {context.hex()}")

def analyze_frequency_patterns(data):
    """Look for frequency storage patterns (typical radio frequencies)"""
    print(f"\n{'='*80}")
    print("FREQUENCY PATTERN ANALYSIS")
    print(f"{'='*80}")

    # VHF/UHF frequencies are typically stored as:
    # - BCD encoded
    # - 32-bit integers (Hz)
    # - Float values (MHz)

    print("\nScanning for potential frequency values (as 32-bit integers):")
    for i in range(0, len(data)-4, 4):
        # Little-endian 32-bit
        freq_int = struct.unpack('<I', data[i:i+4])[0]

        # Check if it looks like a frequency (100-1000 MHz = 100000000-1000000000 Hz)
        if 100000000 <= freq_int <= 1000000000:
            freq_mhz = freq_int / 1000000
            print(f"  Offset {i:#010x}: {freq_int} Hz ({freq_mhz:.4f} MHz)")

            # Show surrounding bytes for context
            context = data[max(0,i-8):i+12]
            print(f"    Context: {context.hex()}")

            if i > 1000:  # Limit output
                print("    ... (stopping after first section)")
                break

def analyze_bit_flags(data, sample_size=10):
    """Analyze potential bit flags in the data"""
    print(f"\n{'='*80}")
    print("BIT FLAG ANALYSIS - Looking for TX enable/disable flags")
    print(f"{'='*80}")

    # Look at the first few potential records
    record_sizes = [40, 48, 56, 64, 80]

    for rec_size in record_sizes:
        if len(data) < rec_size * 3:
            continue

        print(f"\nAssuming {rec_size}-byte records:")
        for rec_num in range(min(sample_size, len(data) // rec_size)):
            offset = rec_num * rec_size
            record = data[offset:offset+rec_size]

            print(f"\n  Record {rec_num} (offset {offset:#010x}):")
            # Show potential flag bytes (typically at start or end of record)
            print(f"    First 8 bytes:  {record[:8].hex()}")
            print(f"    Last 8 bytes:   {record[-8:].hex()}")

            # Look for common flag patterns
            for i, byte in enumerate(record):
                if byte in [0x00, 0x01, 0xFF, 0x80, 0x81]:
                    print(f"    Byte {i}: {byte:#04x} (potential flag)")

def main():
    file_path = Path(r"E:\AI\tk11\TK11.dat")

    print("="*80)
    print("TK11.DAT REVERSE ENGINEERING ANALYSIS")
    print("="*80)
    print(f"Target: {file_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes ({file_path.stat().st_size/1024:.1f} KB)")

    # Read the entire file
    with open(file_path, 'rb') as f:
        data = f.read()

    # 1. Hex dump of first 512 bytes
    hex_dump(data, 0, 512)

    # 2. Extract strings
    print(f"\n{'='*80}")
    print("EXTRACTED STRINGS (min length 4)")
    print(f"{'='*80}")
    strings = find_strings(data, min_length=4)
    for i, s in enumerate(strings[:50]):  # First 50 strings
        print(f"  {i+1}. {s}")
    print(f"\n  ... Total {len(strings)} strings found")

    # 3. Search for keywords
    search_keywords(data)

    # 4. Pattern analysis
    analyze_patterns(data)

    # 5. Frequency analysis
    analyze_frequency_patterns(data)

    # 6. Bit flag analysis
    analyze_bit_flags(data)

    # Additional analysis: File structure
    print(f"\n{'='*80}")
    print("FILE STRUCTURE SUMMARY")
    print(f"{'='*80}")
    print(f"Total file size: {len(data)} bytes")
    print(f"Possible record counts:")
    for rec_size in [32, 40, 48, 56, 64, 80, 96, 128]:
        count = len(data) // rec_size
        remainder = len(data) % rec_size
        print(f"  {rec_size:3d} bytes/record -> {count:4d} records + {remainder:3d} bytes remainder")

if __name__ == "__main__":
    main()
