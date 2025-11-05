#!/usr/bin/env python3
"""
Find the channel index/directory structure in TK11.dat
"""

import struct
from pathlib import Path

def analyze_file_structure(filepath):
    """Deep analysis to find channel organization"""

    with open(filepath, 'rb') as f:
        data = f.read()

    print("="*80)
    print(f"DEEP FILE STRUCTURE ANALYSIS")
    print(f"File: {filepath}")
    print("="*80)

    file_size = len(data)
    print(f"\nFile size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    # Known valid channels in original file
    known_channels = [0, 1, 2, 3, 13]  # Record numbers

    print("\n--- SEARCHING FOR CHANNEL INDEX/TABLE ---")
    print("\nLooking for patterns that reference known channel locations...")

    # Convert record numbers to byte offsets
    record_size = 64
    channel_offsets = [rec * record_size for rec in known_channels]

    print(f"\nKnown channel record numbers: {known_channels}")
    print(f"Known channel byte offsets: {[f'0x{off:08X}' for off in channel_offsets]}")

    # Search for these offsets or record numbers in the file
    print("\n--- SCANNING FOR OFFSET REFERENCES ---")

    found_references = []

    # Search for record numbers as 16-bit or 32-bit integers
    for search_rec in known_channels[:3]:  # Check first 3 channels
        print(f"\nSearching for record number {search_rec}...")

        # As 16-bit little-endian
        search_bytes_u16 = struct.pack('<H', search_rec)
        offset = 0
        while True:
            offset = data.find(search_bytes_u16, offset)
            if offset == -1:
                break
            # Skip if it's in the actual channel record itself
            if offset < file_size - 10000:  # Check only in last part of file
                found_references.append((offset, search_rec, 'u16'))
            offset += 1

    # Look at end of file for possible index
    print("\n--- END OF FILE ANALYSIS ---")
    tail_sizes = [512, 1024, 2048, 4096, 8192]

    for tail_size in tail_sizes:
        if file_size > tail_size:
            tail = data[-tail_size:]

            # Count non-zero bytes
            non_zero = sum(1 for b in tail if b != 0x00 and b != 0xFF)

            if non_zero > tail_size * 0.1:  # More than 10% non-zero
                print(f"\nLast {tail_size} bytes: {non_zero} non-zero bytes ({non_zero/tail_size*100:.1f}%)")
                print(f"Hex dump of last {min(128, tail_size)} bytes:")

                dump_start = max(0, file_size - 128)
                dump_data = data[dump_start:]

                for i in range(0, len(dump_data), 16):
                    hex_str = ' '.join(f'{b:02x}' for b in dump_data[i:i+16])
                    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in dump_data[i:i+16])
                    print(f"  {dump_start+i:08X}: {hex_str:<48} {ascii_str}")
                break

    # Look for potential zone/bank structure
    print("\n--- ANALYZING CHANNEL DISTRIBUTION ---")

    RECORD_SIZE = 64
    num_records = file_size // RECORD_SIZE

    # Track which records are valid
    valid_records = []
    for i in range(num_records):
        offset = i * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]
        freq_bytes = record[0:4]

        # Not empty
        if freq_bytes != b'\xff\xff\xff\xff':
            freq_hz = struct.unpack('<I', freq_bytes)[0]
            # Valid frequency
            if 2_000_000 <= freq_hz <= 2_000_000_000:
                valid_records.append(i)

    print(f"\nTotal valid channel records: {len(valid_records)}")
    print(f"Record numbers (first 20): {valid_records[:20]}")
    print(f"Record numbers (last 10): {valid_records[-10:]}")

    # Look for patterns
    if len(valid_records) > 1:
        gaps = [valid_records[i+1] - valid_records[i] for i in range(len(valid_records)-1)]
        print(f"\nGaps between valid channels (first 20): {gaps[:20]}")

        # Find clusters
        clusters = []
        current_cluster = [valid_records[0]]

        for i in range(1, len(valid_records)):
            if valid_records[i] - valid_records[i-1] < 50:  # Within 50 records
                current_cluster.append(valid_records[i])
            else:
                clusters.append(current_cluster)
                current_cluster = [valid_records[i]]
        clusters.append(current_cluster)

        print(f"\nFound {len(clusters)} clusters of channels:")
        for idx, cluster in enumerate(clusters):
            print(f"  Cluster {idx+1}: Records {cluster[0]}-{cluster[-1]} ({len(cluster)} channels)")

    # Check for channel list bitmap
    print("\n--- LOOKING FOR CHANNEL BITMAP/FLAGS ---")

    # Create a bitmap of which records are used
    bitmap_size = (num_records + 7) // 8  # Bytes needed for bitmap

    print(f"\nIf using bitmap: {bitmap_size} bytes needed for {num_records} records")

    # Search for potential bitmap patterns
    expected_bitmap = bytearray(bitmap_size)
    for rec in valid_records:
        byte_idx = rec // 8
        bit_idx = rec % 8
        expected_bitmap[byte_idx] |= (1 << bit_idx)

    print(f"Expected bitmap pattern (first 32 bytes): {expected_bitmap[:32].hex(' ')}")

    # Search for this pattern
    search_pattern = bytes(expected_bitmap[:16])  # First 16 bytes
    idx = data.find(search_pattern)

    if idx != -1:
        print(f"\n*** FOUND POTENTIAL BITMAP at offset 0x{idx:08X} ***")
    else:
        print(f"\nNo exact bitmap match found")

    # Look for zone/bank table
    print("\n--- SEARCHING FOR ZONE/BANK TABLE ---")

    # TK11.exe might organize channels into zones
    # Look for structures with channel count + channel list

    # Search for byte = 83 (original channel count)
    original_count = 83
    count_bytes = struct.pack('B', original_count)

    print(f"\nSearching for channel count value {original_count} (0x{original_count:02X})...")

    offset = 0
    count_matches = []
    while True:
        offset = data.find(count_bytes, offset)
        if offset == -1:
            break

        # Skip if it's in a channel record
        if offset % 64 >= 24:  # Not in name field
            count_matches.append(offset)

        offset += 1

    if count_matches:
        print(f"Found {len(count_matches)} potential matches:")
        for match_off in count_matches[:10]:
            context = data[match_off-8:match_off+16]
            print(f"  0x{match_off:08X}: {context.hex(' ')}")

def compare_files():
    """Compare original and modified to see what should have changed"""

    print("\n" + "="*80)
    print("COMPARING ORIGINAL VS MODIFIED")
    print("="*80)

    orig_path = Path(r"E:\AI\tk11\TK11.dat")
    mod_path = Path(r"E:\AI\tk11\TK11_CB_FULL_DSB_20251029_145743.dat")

    with open(orig_path, 'rb') as f:
        orig_data = f.read()

    with open(mod_path, 'rb') as f:
        mod_data = f.read()

    print(f"\nOriginal size: {len(orig_data):,} bytes")
    print(f"Modified size: {len(mod_data):,} bytes")

    if len(orig_data) != len(mod_data):
        print("ERROR: Files have different sizes!")
        return

    # Find all differences
    differences = []
    for i in range(len(orig_data)):
        if orig_data[i] != mod_data[i]:
            differences.append(i)

    print(f"\nTotal bytes changed: {len(differences):,}")

    # Group differences by 64-byte record
    records_changed = set()
    for offset in differences:
        record_num = offset // 64
        records_changed.add(record_num)

    print(f"Records modified: {len(records_changed)}")
    print(f"Record numbers: {sorted(records_changed)}")

    # Find differences OUTSIDE channel records
    outside_records = []
    for offset in differences:
        # Check if this offset could be in a "header" or "footer" area
        # that TK11.exe uses to track channels
        record_num = offset // 64
        if record_num > 2000:  # Beyond normal channel area
            outside_records.append(offset)

    if outside_records:
        print(f"\n*** IMPORTANT: {len(outside_records)} bytes changed in non-channel area ***")
        print(f"Offsets: {outside_records[:20]}")
    else:
        print("\nNo changes found outside channel record area")
        print("This means TK11.exe must use a channel INDEX that we didn't update!")

def main():
    orig_path = Path(r"E:\AI\tk11\TK11.dat")
    analyze_file_structure(orig_path)
    compare_files()

    print("\n" + "="*80)
    print("HYPOTHESIS")
    print("="*80)
    print("""
TK11.exe likely uses one of these methods to track channels:

1. CHANNEL COUNT FIELD: A byte/word somewhere that says "I have 83 channels"
   - We added 40 channels but didn't update this counter
   - TK11.exe only reads the first 83 channels

2. CHANNEL INDEX TABLE: A list/array of record numbers to read
   - Example: [0, 1, 2, 3, 13, 14, ...] (83 entries)
   - TK11.exe only looks at channels in this list
   - Our CB channels (rec 4-12, 29-59) aren't in the list

3. ZONE/BANK STRUCTURE: Channels organized into zones
   - Each zone has its own channel list
   - We need to add CB channels to a zone

4. SEQUENTIAL READING: TK11.exe reads sequentially but stops at first gap
   - Original: 0, 1, 2, 3, then GAP at 4-12, then 13...
   - We filled the gap with CB channels
   - But TK11.exe might have stopped reading at record 83

NEXT STEP: Find and update the channel index/count structure!
""")

if __name__ == "__main__":
    main()
