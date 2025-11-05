#!/usr/bin/env python3
"""
Analyze where CB channels were written and why TK11.exe doesn't see them
"""

import struct
from pathlib import Path

RECORD_SIZE = 64

def analyze_file(filepath, name):
    """Analyze a TK11.dat file structure"""
    print("="*80)
    print(f"ANALYZING: {name}")
    print(f"File: {filepath}")
    print("="*80)

    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"\nFile size: {len(data):,} bytes ({len(data)/1024:.1f} KB)")
    print(f"Record size: {RECORD_SIZE} bytes")
    print(f"Total records: {len(data) // RECORD_SIZE}")

    # Check file header (first 256 bytes)
    print("\n--- FILE HEADER (first 256 bytes) ---")
    header = data[0:256]

    # Look for magic bytes or signature
    print(f"First 16 bytes (hex): {header[0:16].hex(' ')}")
    print(f"First 16 bytes (ascii): {repr(header[0:16])}")

    # Look for possible channel count indicator
    print("\nSearching for potential channel count fields...")
    for offset in [0, 4, 8, 12, 16, 20, 24, 28, 32]:
        val_u16 = struct.unpack('<H', data[offset:offset+2])[0]
        val_u32 = struct.unpack('<I', data[offset:offset+4])[0]
        print(f"  Offset {offset:3d}: u16={val_u16:6d} (0x{val_u16:04X})  u32={val_u32:10d} (0x{val_u32:08X})")

    # Scan all records
    print("\n--- SCANNING ALL RECORDS ---")

    valid_channels = []
    empty_slots = []
    cb_channels = []

    for i in range(len(data) // RECORD_SIZE):
        offset = i * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        # Get frequency
        freq_bytes = record[0:4]

        # Empty slot check (all 0xFF)
        if freq_bytes == b'\xff\xff\xff\xff':
            empty_slots.append(i)
            continue

        # Decode frequency
        freq_hz = struct.unpack('<I', freq_bytes)[0]

        # Valid frequency range check (2 MHz - 2000 MHz)
        if 2_000_000 <= freq_hz <= 2_000_000_000:
            # Get channel name
            name_bytes = record[24:40]
            name = name_bytes.decode('ascii', errors='ignore').rstrip('\x00')

            # Get mode and TX permit
            tx_permit = record[22]
            mode = record[23]

            channel_info = {
                'record_num': i,
                'offset': offset,
                'freq_hz': freq_hz,
                'freq_mhz': freq_hz / 1e6,
                'name': name,
                'tx_permit': tx_permit,
                'mode': mode,
            }

            valid_channels.append(channel_info)

            # Check if CB band (26.965 - 27.405 MHz)
            if 26_965_000 <= freq_hz <= 27_405_000:
                cb_channels.append(channel_info)

    print(f"\nTotal valid channels: {len(valid_channels)}")
    print(f"Total empty slots: {len(empty_slots)}")
    print(f"Total CB channels (26.965-27.405 MHz): {len(cb_channels)}")

    if empty_slots:
        print(f"\nFirst 10 empty slots: {empty_slots[:10]}")
        print(f"Last 10 empty slots: {empty_slots[-10:]}")

    # Show CB channels
    if cb_channels:
        print("\n--- CB CHANNELS FOUND ---")
        for ch in cb_channels:
            print(f"Record {ch['record_num']:5d} @ 0x{ch['offset']:08X}: "
                  f"{ch['freq_mhz']:8.4f} MHz  "
                  f"Mode=0x{ch['mode']:02X}  TX=0x{ch['tx_permit']:02X}  "
                  f"Name='{ch['name']}'")
    else:
        print("\n*** NO CB CHANNELS FOUND ***")

    # Show first and last valid channels
    if valid_channels:
        print("\n--- FIRST 5 VALID CHANNELS ---")
        for ch in valid_channels[:5]:
            print(f"Record {ch['record_num']:5d}: {ch['freq_mhz']:8.4f} MHz - '{ch['name']}'")

        print("\n--- LAST 5 VALID CHANNELS ---")
        for ch in valid_channels[-5:]:
            print(f"Record {ch['record_num']:5d}: {ch['freq_mhz']:8.4f} MHz - '{ch['name']}'")

    print("\n")
    return {
        'valid_channels': len(valid_channels),
        'empty_slots': len(empty_slots),
        'cb_channels': cb_channels,
        'first_empty': empty_slots[0] if empty_slots else None,
    }

def main():
    base_path = Path(r"E:\AI\tk11")

    # Analyze original
    original = base_path / "TK11.dat"
    original_info = analyze_file(original, "ORIGINAL TK11.dat")

    # Analyze modified with CB channels
    modified = base_path / "TK11_CB_FULL_DSB_20251029_145743.dat"
    if modified.exists():
        modified_info = analyze_file(modified, "MODIFIED (CB Full DSB)")

        # Compare
        print("\n" + "="*80)
        print("COMPARISON")
        print("="*80)
        print(f"Original valid channels: {original_info['valid_channels']}")
        print(f"Modified valid channels: {modified_info['valid_channels']}")
        print(f"Difference: {modified_info['valid_channels'] - original_info['valid_channels']} channels added")

        print(f"\nOriginal CB channels: {len(original_info['cb_channels'])}")
        print(f"Modified CB channels: {len(modified_info['cb_channels'])}")

        if modified_info['cb_channels']:
            print(f"\n✅ SUCCESS: CB channels were written to the file!")
            print(f"\nFirst empty slot used: Record {original_info['first_empty']}")
            print(f"CB channels placed starting at: Record {modified_info['cb_channels'][0]['record_num']}")
        else:
            print(f"\n❌ PROBLEM: CB channels NOT found in modified file")
    else:
        print(f"\n⚠️  Modified file not found: {modified}")

if __name__ == "__main__":
    main()
