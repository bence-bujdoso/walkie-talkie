#!/usr/bin/env python3
"""
TK11 Channel TX Permit Patcher
Finds and enables TX for specific channels (like K38 USB)
"""

import sys
import struct

def find_channel_by_name(dat_file_path, channel_name):
    """
    Find a channel by its name in the .dat file

    Returns: list of (offset, channel_data) tuples
    """
    RECORD_SIZE = 64
    NAME_OFFSET = 0x18  # Channel name starts at byte 24 in each record
    NAME_SIZE = 16

    with open(dat_file_path, 'rb') as f:
        data = f.read()

    file_size = len(data)
    num_records = file_size // RECORD_SIZE

    matches = []
    target_name = channel_name.encode('ascii').ljust(NAME_SIZE, b'\x00')

    print(f"🔍 Searching for channel: '{channel_name}'")
    print(f"   File size: {file_size:,} bytes")
    print(f"   Total records: {num_records:,}")
    print()

    for i in range(num_records):
        offset = i * RECORD_SIZE
        record = data[offset:offset + RECORD_SIZE]

        # Get channel name
        name_bytes = record[NAME_OFFSET:NAME_OFFSET + NAME_SIZE]

        # Check if it matches (partial match)
        if channel_name.encode('ascii') in name_bytes:
            name_str = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')

            # Get frequency
            freq_hz = struct.unpack('<I', record[0:4])[0]
            freq_mhz = freq_hz / 1_000_000.0

            # Get TX permit flag
            tx_permit = record[0x16]

            print(f"✅ FOUND at record {i} (offset 0x{offset:08X}):")
            print(f"   Name: '{name_str}'")
            print(f"   Frequency: {freq_mhz:.4f} MHz")
            print(f"   TX Permit (byte 22): 0x{tx_permit:02X} ({tx_permit})")
            if tx_permit == 0xFF:
                print(f"   Status: TX ENABLED ✓")
            elif tx_permit == 0x00:
                print(f"   Status: TX DISABLED ✗")
            else:
                print(f"   Status: RESTRICTED/UNKNOWN")
            print()

            matches.append((offset, record, tx_permit))

    return matches

def patch_channel_tx_permit(dat_file_path, channel_name):
    """
    Find channel by name and enable TX (set byte 22 to 0xFF)
    """

    print("="*70)
    print("TK11 Channel TX Permit Patcher")
    print("="*70)
    print()

    # Find the channel
    matches = find_channel_by_name(dat_file_path, channel_name)

    if not matches:
        print(f"❌ Channel '{channel_name}' not found!")
        return False

    # Read the file
    with open(dat_file_path, 'rb') as f:
        data = bytearray(f.read())

    # Patch all matching channels
    patched_count = 0
    for offset, record, current_tx in matches:
        tx_permit_offset = offset + 0x16  # Byte 22 in the record

        if current_tx == 0xFF:
            print(f"ℹ️  Channel at 0x{offset:08X} already has TX enabled (0xFF)")
            continue

        # Patch it
        data[tx_permit_offset] = 0xFF
        patched_count += 1

        print(f"✅ PATCHED channel at 0x{offset:08X}:")
        print(f"   TX Permit: 0x{current_tx:02X} → 0xFF")
        print(f"   Status: TX NOW ENABLED! ✓")
        print()

    if patched_count == 0:
        print("ℹ️  No changes needed - all matching channels already have TX enabled!")
        return True

    # Save patched file
    output_file = dat_file_path.replace('.dat', '_TX_ENABLED.dat')
    if output_file == dat_file_path:
        output_file = dat_file_path + '_TX_ENABLED'

    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"💾 Patched file saved: {output_file}")
    print()
    print(f"📋 Next Steps:")
    print(f"   1. Open TK11.exe")
    print(f"   2. Click 'Write' / 'Upload to radio'")
    print(f"   3. Select: {output_file}")
    print(f"   4. Wait for completion")
    print(f"   5. Test TX on {channel_name} - should work now! ✅")

    return True

def scan_all_channels(dat_file_path):
    """
    Scan all channels and show TX permit status
    """
    RECORD_SIZE = 64
    NAME_OFFSET = 0x18
    NAME_SIZE = 16

    with open(dat_file_path, 'rb') as f:
        data = f.read()

    file_size = len(data)
    num_records = file_size // RECORD_SIZE

    print("="*70)
    print("TK11 Channel Scanner - TX Permit Status")
    print("="*70)
    print()

    disabled_count = 0
    enabled_count = 0

    print(f"{'Record':<8} {'Offset':<12} {'Frequency':<15} {'TX':<6} {'Name':<20}")
    print("-" * 70)

    for i in range(min(num_records, 100)):  # Scan first 100 channels
        offset = i * RECORD_SIZE
        record = data[offset:offset + RECORD_SIZE]

        # Check if record is empty (all 0xFF)
        if record == b'\xFF' * RECORD_SIZE:
            continue

        # Get frequency
        freq_hz = struct.unpack('<I', record[0:4])[0]
        if freq_hz == 0 or freq_hz == 0xFFFFFFFF:
            continue

        freq_mhz = freq_hz / 1_000_000.0

        # Get TX permit
        tx_permit = record[0x16]

        # Get name
        name_bytes = record[NAME_OFFSET:NAME_OFFSET + NAME_SIZE]
        name_str = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')

        # Status
        if tx_permit == 0xFF:
            status = "✓ YES"
            enabled_count += 1
        elif tx_permit == 0x00:
            status = "✗ NO"
            disabled_count += 1
        else:
            status = f"? 0x{tx_permit:02X}"

        print(f"{i:<8} 0x{offset:08X}  {freq_mhz:>10.4f} MHz  {status:<6} {name_str:<20}")

    print()
    print(f"Summary (first 100 records):")
    print(f"  TX Enabled:  {enabled_count}")
    print(f"  TX Disabled: {disabled_count}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  Patch channel:  python {sys.argv[0]} <file.dat> <channel_name>")
        print(f"  Scan channels:  python {sys.argv[0]} --scan <file.dat>")
        print()
        print("Examples:")
        print(f"  python {sys.argv[0]} TK11_BACKUP.dat 'K38 USB'")
        print(f"  python {sys.argv[0]} --scan TK11_BACKUP.dat")
        sys.exit(1)

    if sys.argv[1] == '--scan':
        if len(sys.argv) < 3:
            print("Error: Specify .dat file to scan")
            sys.exit(1)
        scan_all_channels(sys.argv[2])
    else:
        dat_file = sys.argv[1]
        channel_name = sys.argv[2] if len(sys.argv) > 2 else "K38 USB"
        success = patch_channel_tx_permit(dat_file, channel_name)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
