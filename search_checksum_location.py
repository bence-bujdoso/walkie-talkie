#!/usr/bin/env python3
"""
Search for checksum storage location in firmware
The TK11.exe likely validates a stored checksum against calculated checksum
"""

from pathlib import Path
import struct

def search_checksum_storage(firmware_path):
    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print("SEARCHING FOR CHECKSUM STORAGE LOCATION")
    print("="*80)

    # Calculate checksums for the file (excluding potential checksum bytes)
    print("\nCalculating various checksums...")

    # Method 1: Sum of all bytes except last 4
    sum_minus_4 = sum(data[:-4]) & 0xFFFFFFFF
    print(f"Sum (excluding last 4 bytes): 0x{sum_minus_4:08X}")

    # Method 2: Sum of all bytes except last 8
    sum_minus_8 = sum(data[:-8]) & 0xFFFFFFFF
    print(f"Sum (excluding last 8 bytes): 0x{sum_minus_8:08X}")

    # Method 3: Check if last 4 bytes match a checksum
    last_4 = struct.unpack('<I', data[-4:])[0]
    last_4_be = struct.unpack('>I', data[-4:])[0]
    print(f"\nLast 4 bytes (LE): 0x{last_4:08X}")
    print(f"Last 4 bytes (BE): 0x{last_4_be:08X}")

    # Method 4: Try different checksum algorithms
    print("\n" + "="*80)
    print("TRYING DIFFERENT CHECKSUM ALGORITHMS")
    print("="*80)

    # Test with data excluding last 4 bytes
    test_data = data[:-4]

    # Simple sum
    simple_sum = sum(test_data) & 0xFFFFFFFF
    print(f"\n1. Simple sum: 0x{simple_sum:08X}")

    # Two's complement
    twos_comp = (~simple_sum + 1) & 0xFFFFFFFF
    print(f"2. Two's complement: 0x{twos_comp:08X}")

    # Negation
    negation = (~simple_sum) & 0xFFFFFFFF
    print(f"3. Negation: 0x{negation:08X}")

    # XOR
    xor_sum = 0
    for b in test_data:
        xor_sum ^= b
    print(f"4. XOR sum: 0x{xor_sum:02X}")

    # Check common checksum positions
    print("\n" + "="*80)
    print("CHECKING COMMON CHECKSUM STORAGE LOCATIONS")
    print("="*80)

    positions = [
        (len(data) - 4, "Last 4 bytes"),
        (len(data) - 8, "Last 8 bytes (first 4)"),
        (len(data) - 16, "Last 16 bytes (first 4)"),
        (0, "First 4 bytes"),
        (4, "Bytes 4-7"),
        (8, "Bytes 8-11"),
    ]

    for pos, desc in positions:
        if pos >= 0 and pos + 4 <= len(data):
            val_le = struct.unpack('<I', data[pos:pos+4])[0]
            val_be = struct.unpack('>I', data[pos:pos+4])[0]

            print(f"\n{desc} (offset 0x{pos:08X}):")
            print(f"  LE: 0x{val_le:08X}")
            print(f"  BE: 0x{val_be:08X}")

            # Check if it matches any calculated checksum
            if val_le == simple_sum:
                print("  *** MATCH: Simple sum (LE) ***")
            if val_be == simple_sum:
                print("  *** MATCH: Simple sum (BE) ***")
            if val_le == twos_comp:
                print("  *** MATCH: Two's complement (LE) ***")
            if val_be == twos_comp:
                print("  *** MATCH: Two's complement (BE) ***")

    # Search for the calculated checksum value in the file
    print("\n" + "="*80)
    print("SEARCHING FOR CHECKSUM VALUE IN FILE")
    print("="*80)

    # Search for simple sum (little endian)
    sum_bytes = struct.pack('<I', simple_sum)
    offset = data.find(sum_bytes)
    if offset != -1:
        print(f"\nFound sum 0x{simple_sum:08X} (LE) at offset 0x{offset:08X}")
    else:
        print(f"\nSum 0x{simple_sum:08X} (LE) not found in file")

    # Search for simple sum (big endian)
    sum_bytes_be = struct.pack('>I', simple_sum)
    offset = data.find(sum_bytes_be)
    if offset != -1:
        print(f"Found sum 0x{simple_sum:08X} (BE) at offset 0x{offset:08X}")
    else:
        print(f"Sum 0x{simple_sum:08X} (BE) not found in file")

    return simple_sum, last_4

def fix_checksum(input_path, output_path):
    """Try to fix the checksum in the patched firmware"""

    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print("\n" + "="*80)
    print("ATTEMPTING CHECKSUM FIX")
    print("="*80)

    # Assume checksum is stored in last 4 bytes (common practice)
    # Calculate correct checksum for data excluding last 4 bytes

    calc_sum = sum(data[:-4]) & 0xFFFFFFFF

    print(f"\nCalculated checksum: 0x{calc_sum:08X}")

    current_last_4 = struct.unpack('<I', data[-4:])[0]
    print(f"Current last 4 bytes: 0x{current_last_4:08X}")

    # Store the new checksum (try little-endian first)
    struct.pack_into('<I', data, len(data) - 4, calc_sum)

    print(f"Updated last 4 bytes to: 0x{calc_sum:08X}")

    # Write output
    with open(output_path, 'wb') as f:
        f.write(data)

    print(f"\n[OK] Fixed firmware written to: {output_path.name}")

    return True

if __name__ == "__main__":
    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    patched = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin")

    print("="*80)
    print("ANALYZING ORIGINAL FIRMWARE")
    print("="*80)
    search_checksum_storage(original)

    print("\n\n")
    print("="*80)
    print("ANALYZING PATCHED FIRMWARE")
    print("="*80)
    search_checksum_storage(patched)

    print("\n\n")
    print("="*80)
    print("ATTEMPTING TO FIX PATCHED FIRMWARE")
    print("="*80)

    fixed_output = Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin")
    fix_checksum(patched, fixed_output)

    print("\n" + "="*80)
    print("VERIFYING FIXED FIRMWARE")
    print("="*80)
    search_checksum_storage(fixed_output)
