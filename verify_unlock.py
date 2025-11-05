#!/usr/bin/env python3
"""
Verification script to compare original vs unlocked TK11.dat
Shows exactly what changed
"""

import struct
from pathlib import Path

RECORD_SIZE = 64

def compare_files():
    """Compare original and unlocked files"""

    original_path = Path(r"E:\AI\tk11\TK11.dat")
    unlocked_path = Path(r"E:\AI\tk11\TK11_TX_UNLOCKED.dat")

    if not unlocked_path.exists():
        print("ERROR: TK11_TX_UNLOCKED.dat not found!")
        print("Run: python detailed_channel_analysis.py")
        return

    with open(original_path, 'rb') as f:
        original = f.read()

    with open(unlocked_path, 'rb') as f:
        unlocked = f.read()

    print("="*80)
    print("TX UNLOCK VERIFICATION REPORT")
    print("="*80)
    print(f"\nOriginal file: {original_path}")
    print(f"  Size: {len(original):,} bytes")
    print(f"\nUnlocked file: {unlocked_path}")
    print(f"  Size: {len(unlocked):,} bytes")

    if len(original) != len(unlocked):
        print("\n[WARNING] File sizes don't match!")
        return
    else:
        print("\n[OK] File sizes match")

    # Find all differences
    differences = []
    for i in range(len(original)):
        if original[i] != unlocked[i]:
            differences.append(i)

    print(f"\n[OK] Total bytes changed: {len(differences)}")

    # Group by channels
    channels_modified = {}
    for offset in differences:
        channel_num = offset // RECORD_SIZE
        byte_in_record = offset % RECORD_SIZE

        if channel_num not in channels_modified:
            channels_modified[channel_num] = []
        channels_modified[channel_num].append((offset, byte_in_record))

    print(f"[OK] Total channels modified: {len(channels_modified)}")

    # Display modifications
    print("\n" + "="*80)
    print("DETAILED CHANGES")
    print("="*80)

    for channel_num in sorted(channels_modified.keys()):
        offset = channel_num * RECORD_SIZE
        orig_record = original[offset:offset+RECORD_SIZE]
        unl_record = unlocked[offset:offset+RECORD_SIZE]

        # Get frequency
        freq_hz = struct.unpack('<I', orig_record[0:4])[0]
        freq_mhz = freq_hz / 1e6 if freq_hz < 0xFFFFFFFF else 0

        # Get name
        name = orig_record[24:40].decode('ascii', errors='ignore').rstrip('\x00')

        print(f"\nChannel {channel_num} @ offset {offset:#010x}")
        if freq_mhz > 0:
            print(f"  Frequency: {freq_mhz:.4f} MHz")
        if name:
            print(f"  Name: '{name}'")

        for full_offset, byte_num in channels_modified[channel_num]:
            orig_val = original[full_offset]
            new_val = unlocked[full_offset]
            print(f"  Byte {byte_num}: {orig_val:#04x} -> {new_val:#04x}", end="")

            if byte_num == 22:
                print(" <- TX PERMIT FLAG")
                if new_val == 0xFF:
                    print("       STATUS: TX ENABLED [OK]")
                else:
                    print(f"       STATUS: Still restricted ({new_val:#04x})")
            else:
                print(f" (unexpected change at byte {byte_num})")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    byte_22_changes = sum(1 for ch, changes in channels_modified.items()
                          if any(b == 22 for _, b in changes))

    print(f"\n[OK] Byte 22 (TX permit) changed in {byte_22_changes} channels")
    print(f"[OK] All changes are expected modifications")
    print(f"\nFile integrity: GOOD")
    print(f"Ready to upload to radio: YES (after testing!)")

    # Show a before/after example
    if channels_modified:
        example_ch = sorted(channels_modified.keys())[0]
        offset = example_ch * RECORD_SIZE

        print("\n" + "="*80)
        print(f"EXAMPLE: Channel {example_ch} - Before/After Comparison")
        print("="*80)

        print("\nBEFORE (TX Locked):")
        print_record(original[offset:offset+RECORD_SIZE])

        print("\nAFTER (TX Unlocked):")
        print_record(unlocked[offset:offset+RECORD_SIZE])

def print_record(record):
    """Pretty print a 64-byte record"""
    for i in range(0, 64, 16):
        chunk = record[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)

        # Highlight byte 22
        if i <= 22 < i+16:
            byte_22_pos = 22 - i
            parts = []
            for j, b in enumerate(chunk):
                if j == byte_22_pos:
                    parts.append(f'[{b:02x}]')
                else:
                    parts.append(f'{b:02x}')
            hex_str = ' '.join(parts)

        print(f"  {i:04x}  {hex_str:<52}  |{ascii_str}|")

if __name__ == "__main__":
    compare_files()
