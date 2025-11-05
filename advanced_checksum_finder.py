#!/usr/bin/env python3
"""
Advanced firmware checksum algorithm finder
Try many different checksum algorithms to find the correct one
"""

import struct
import hashlib
import zlib
from pathlib import Path

def crc16_ccitt(data):
    """CRC16-CCITT"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
        crc &= 0xFFFF
    return crc

def crc16_modbus(data):
    """CRC16-MODBUS"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc = crc >> 1
    return crc

def crc32_reversed(data):
    """CRC32 with reversed bit order"""
    crc = zlib.crc32(data) & 0xFFFFFFFF
    # Reverse bits
    result = 0
    for i in range(32):
        if crc & (1 << i):
            result |= (1 << (31 - i))
    return result

def simple_xor_checksum(data):
    """Simple XOR of all bytes"""
    result = 0
    for byte in data:
        result ^= byte
    return result

def fletcher32(data):
    """Fletcher-32 checksum"""
    sum1 = 0xFFFF
    sum2 = 0xFFFF

    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            word = struct.unpack('<H', data[i:i+2])[0]
        else:
            word = data[i]

        sum1 = (sum1 + word) % 0xFFFF
        sum2 = (sum2 + sum1) % 0xFFFF

    return (sum2 << 16) | sum1

def adler32(data):
    """Adler-32 checksum"""
    return zlib.adler32(data) & 0xFFFFFFFF

def analyze_original_firmware(firmware_path):
    """Extract potential checksum values from original firmware"""

    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print("ANALYZING ORIGINAL FIRMWARE HEADER")
    print("="*80)

    # Extract all 32-bit values from first 256 bytes
    print("\nAll 32-bit values in first 256 bytes (potential checksums):")

    potential_checksums = []

    for offset in range(0, 256, 4):
        value_le = struct.unpack('<I', data[offset:offset+4])[0]
        value_be = struct.unpack('>I', data[offset:offset+4])[0]

        potential_checksums.append({
            'offset': offset,
            'value_le': value_le,
            'value_be': value_be
        })

        if offset % 16 == 0:
            print(f"\n  0x{offset:04X}:", end="")
        print(f" {value_le:08X}", end="")

    print("\n")
    return data, potential_checksums

def try_all_checksum_algorithms(data, potential_locations):
    """Try many different checksum algorithms and data ranges"""

    print("="*80)
    print("TRYING ADVANCED CHECKSUM ALGORITHMS")
    print("="*80)

    # Different data ranges to calculate checksum over
    ranges = [
        ('Full firmware', 0, len(data)),
        ('Skip header 64', 64, len(data)),
        ('Skip header 128', 128, len(data)),
        ('Skip header 256', 256, len(data)),
        ('Skip first 4 bytes', 4, len(data)),
        ('Skip first 16 bytes', 16, len(data)),
    ]

    # Checksum algorithms to try
    algorithms = [
        ('CRC32', lambda d: zlib.crc32(d) & 0xFFFFFFFF),
        ('CRC32 reversed', crc32_reversed),
        ('Adler32', adler32),
        ('Fletcher32', fletcher32),
        ('Simple sum', lambda d: sum(d) & 0xFFFFFFFF),
        ('Simple sum 16-bit', lambda d: sum(d) & 0xFFFF),
        ('XOR checksum', lambda d: simple_xor_checksum(d) & 0xFFFFFFFF),
        ('MD5 first 4 bytes', lambda d: struct.unpack('<I', hashlib.md5(d).digest()[:4])[0]),
        ('SHA1 first 4 bytes', lambda d: struct.unpack('<I', hashlib.sha1(d).digest()[:4])[0]),
        ('CRC16 CCITT', lambda d: crc16_ccitt(d)),
        ('CRC16 MODBUS', lambda d: crc16_modbus(d)),
    ]

    matches = []

    for range_name, start, end in ranges:
        data_range = data[start:end]

        for algo_name, algo_func in algorithms:
            try:
                checksum = algo_func(data_range)

                # Check if this matches any potential location
                for pot in potential_locations:
                    if pot['value_le'] == checksum or pot['value_be'] == checksum:
                        endian = 'LE' if pot['value_le'] == checksum else 'BE'
                        match = {
                            'offset': pot['offset'],
                            'algorithm': algo_name,
                            'range': range_name,
                            'checksum': checksum,
                            'endian': endian
                        }
                        matches.append(match)
                        print(f"\n[MATCH FOUND!]")
                        print(f"  Offset: 0x{pot['offset']:04X}")
                        print(f"  Algorithm: {algo_name}")
                        print(f"  Data range: {range_name}")
                        print(f"  Checksum: 0x{checksum:08X}")
                        print(f"  Endian: {endian}")
            except Exception as e:
                pass

    return matches

def create_fixed_firmware_with_algorithm(original_data, patched_data, match, output_path):
    """Create fixed firmware using found algorithm"""

    print("="*80)
    print(f"CREATING FIXED FIRMWARE WITH MATCHED ALGORITHM")
    print("="*80)

    print(f"\nUsing:")
    print(f"  Algorithm: {match['algorithm']}")
    print(f"  Checksum location: 0x{match['offset']:04X}")
    print(f"  Data range: {match['range']}")
    print(f"  Endian: {match['endian']}")

    # TODO: Implement based on matched algorithm
    # This is just a placeholder
    print("\nThis would create the properly fixed firmware...")

def main():
    base_path = Path(r"E:\AI\tk11")

    original_fw = base_path / "TK11_v5.00.09_ENG.bin"

    print("="*80)
    print("ADVANCED CHECKSUM ALGORITHM FINDER")
    print("="*80)
    print("\nAnalyzing original firmware to find checksum algorithm...")

    original_data, potential_checksums = analyze_original_firmware(original_fw)

    # Try all algorithms
    matches = try_all_checksum_algorithms(original_data, potential_checksums)

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    if matches:
        print(f"\nFound {len(matches)} potential checksum algorithm matches!")
        print("\nMatches:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. Offset 0x{match['offset']:04X}")
            print(f"   Algorithm: {match['algorithm']}")
            print(f"   Range: {match['range']}")
            print(f"   Endian: {match['endian']}")
    else:
        print("\nNo matches found.")
        print("\nThe checksum algorithm is likely:")
        print("  - Custom/proprietary algorithm")
        print("  - Using a non-standard polynomial")
        print("  - Encrypted or obfuscated")
        print("\nNext steps:")
        print("  1. Reverse engineer TK11.exe with dnSpy/ILSpy")
        print("  2. Look for firmware validation code")
        print("  3. Extract exact checksum calculation")

if __name__ == "__main__":
    main()
