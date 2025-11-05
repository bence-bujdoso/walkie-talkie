#!/usr/bin/env python3
"""
Extract and analyze TX restriction regions in firmware
Focus on finding the exact code that enables/disables TX per mode
"""

def hexdump(data, offset=0, length=256):
    """Generate a hex dump with ASCII"""
    lines = []
    for i in range(0, min(length, len(data)), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"0x{offset+i:08X}:  {hex_part:<48}  {ascii_part}")
    return '\n'.join(lines)

def analyze_tx_region(data, tx_pos):
    """Deep analysis around TX keyword"""
    print(f"\n{'='*80}")
    print(f"TX REGION ANALYSIS @ 0x{tx_pos:08X}")
    print(f"{'='*80}")

    # Extract large region
    start = max(0, tx_pos - 256)
    end = min(len(data), tx_pos + 256)
    region = data[start:end]

    print("\nHex dump of region:")
    print(hexdump(region, start, 512))

    # Look for mode values near TX
    print(f"\n\nMode-related bytes near TX:")
    for i in range(max(0, tx_pos-64), min(len(data), tx_pos+64)):
        byte = data[i]
        if byte <= 0x04:  # Potential mode index
            offset_from_tx = i - tx_pos
            print(f"  @ 0x{i:08X} ({offset_from_tx:+4d} from TX): 0x{byte:02x} ({byte})")

    # Look for flag bytes
    print(f"\n\nFlag bytes near TX (0x03, 0x1F patterns):")
    for i in range(max(0, tx_pos-128), min(len(data), tx_pos+128)):
        byte = data[i]
        if byte in [0x03, 0x07, 0x0F, 0x1F]:
            offset_from_tx = i - tx_pos
            print(f"  @ 0x{i:08X} ({offset_from_tx:+4d} from TX): 0x{byte:02x} ({bin(byte)}) - potential mode flag")

    # Look for nearby strings
    print(f"\n\nNearby strings:")
    search_region = data[max(0, tx_pos-512):min(len(data), tx_pos+512)]
    for keyword in [b'FM', b'AM', b'CW', b'USB', b'LSB', b'RX', b'DISABLE', b'LOCK', b'ENABLE']:
        pos = search_region.find(keyword)
        if pos != -1:
            actual_pos = max(0, tx_pos-512) + pos
            offset_from_tx = actual_pos - tx_pos
            print(f"  '{keyword.decode('ascii')}' @ 0x{actual_pos:08X} ({offset_from_tx:+4d} from TX)")

def analyze_disable_message_region(data):
    """Find the DISABLE message and surrounding code"""
    print(f"\n{'='*80}")
    print("SEARCHING FOR 'DISABLE' MESSAGE")
    print(f"{'='*80}")

    disable_patterns = [b'DISABLE', b'Disable', b'disable', b'LOCK', b'Lock']

    for pattern in disable_patterns:
        offset = 0
        while True:
            pos = data.find(pattern, offset)
            if pos == -1:
                break

            print(f"\n\nFound '{pattern.decode('ascii')}' @ 0x{pos:08X}")

            # Show context
            context = data[max(0, pos-64):min(len(data), pos+len(pattern)+64)]
            print(f"\nContext:")
            print(hexdump(context, max(0, pos-64), 128))

            # Check for TX/mode references nearby
            nearby = data[max(0, pos-256):min(len(data), pos+256)]
            nearby_keywords = []
            for kw in [b'TX', b'FM', b'AM', b'CW', b'USB', b'LSB']:
                if kw in nearby:
                    nearby_keywords.append(kw.decode('ascii'))

            if nearby_keywords:
                print(f"\n  Nearby keywords: {', '.join(nearby_keywords)}")

            offset = pos + 1

def analyze_mode_check_patterns(data):
    """Find mode validation/checking code patterns"""
    print(f"\n{'='*80}")
    print("MODE VALIDATION CODE PATTERNS")
    print(f"{'='*80}")

    print("\nSearching for mode comparison patterns...")
    print("Looking for: CMP mode, #0x00 (FM) / CMP mode, #0x01 (AM) sequences")

    # ARM Thumb instruction patterns for comparisons
    # CMP Rn, #imm8 is often encoded as: 0x28-0x2F followed by immediate

    # Look for sequences that compare with 0, 1, 2, 3, 4 (mode indices)
    candidates = []

    for i in range(len(data) - 16):
        chunk = data[i:i+16]

        # Look for comparison patterns
        # Pattern: multiple small values (0-4) with surrounding code
        mode_compares = []
        for j in range(16):
            if chunk[j] <= 0x04:
                mode_compares.append((j, chunk[j]))

        # If we have 3+ potential mode values, investigate
        if len(mode_compares) >= 3:
            # Check if there's TX/RX nearby
            nearby = data[max(0, i-256):min(len(data), i+256)]
            if b'TX' in nearby or b'RX' in nearby:
                candidates.append((i, chunk, mode_compares))

    print(f"\nFound {len(candidates)} potential mode validation regions")
    print("\nTop 10 candidates:")

    for idx, (pos, chunk, mode_vals) in enumerate(candidates[:10]):
        print(f"\n  Candidate {idx+1} @ 0x{pos:08X}:")
        print(f"    Hex: {' '.join(f'{b:02x}' for b in chunk)}")
        print(f"    Mode values: {[v[1] for v in mode_vals]}")

        # Show larger context
        context_start = max(0, pos-32)
        context = data[context_start:pos+48]
        print(f"    Context:")
        for line in hexdump(context, context_start, 80).split('\n')[:3]:
            print(f"    {line}")

def extract_channel_mode_field(dat_data):
    """Analyze channel records to find mode field location"""
    print(f"\n{'='*80}")
    print("CHANNEL RECORD MODE FIELD ANALYSIS")
    print(f"{'='*80}")

    # From previous analysis, found "K38 USB" string at record 2
    # Let's analyze 32-byte records
    record_size = 32

    print(f"\nAnalyzing as {record_size}-byte records...")

    # Look for channel name strings
    for i in range(0, min(len(dat_data), 10000), record_size):
        record = dat_data[i:i+record_size]

        # Check if this record contains ASCII channel name
        ascii_parts = []
        for j in range(record_size):
            if 32 <= record[j] < 127:
                ascii_parts.append(chr(record[j]))
            else:
                ascii_parts.append('.')

        ascii_str = ''.join(ascii_parts)

        # If we find a recognizable channel name
        if 'USB' in ascii_str or 'LSB' in ascii_str or 'FM' in ascii_str or 'AM' in ascii_str:
            print(f"\n  Record @ offset 0x{i:08X} (record {i//record_size}):")
            print(f"    Hex:   {' '.join(f'{b:02x}' for b in record)}")
            print(f"    ASCII: {ascii_str}")

            # Identify mode field
            # Typically mode field is 1 byte, values 0-4
            print(f"    Possible mode fields:")
            for j in range(record_size):
                if record[j] <= 0x04:
                    print(f"      Offset +{j}: 0x{record[j]:02x} ({record[j]})")

def main():
    print("="*80)
    print("TK-11 TX RESTRICTION CODE EXTRACTION")
    print("Deep analysis of TX enable/disable implementation")
    print("="*80)

    # Load firmware
    with open('E:\\AI\\tk11\\TK11_v5.00.09_ENG.bin', 'rb') as f:
        fw_data = f.read()

    print(f"\nFirmware size: {len(fw_data)} bytes")

    # Get TX keyword positions
    tx_positions = []
    offset = 0
    while True:
        pos = fw_data.find(b'TX', offset)
        if pos == -1:
            break
        tx_positions.append(pos)
        offset = pos + 1

    print(f"Found {len(tx_positions)} TX keyword occurrences")

    # Analyze first 3 TX regions in detail
    print("\n" + "="*80)
    print("DETAILED TX REGION ANALYSIS (First 3)")
    print("="*80)

    for i, pos in enumerate(tx_positions[:3]):
        analyze_tx_region(fw_data, pos)

    # Search for DISABLE messages
    analyze_disable_message_region(fw_data)

    # Find mode validation patterns
    analyze_mode_check_patterns(fw_data)

    # Analyze DAT file
    print("\n" + "="*80)
    print("DAT FILE ANALYSIS")
    print("="*80)

    try:
        with open('E:\\AI\\tk11\\TK11.dat', 'rb') as f:
            dat_data = f.read()
        print(f"\nDAT file size: {len(dat_data)} bytes")
        extract_channel_mode_field(dat_data)
    except FileNotFoundError:
        print("\nTK11.dat not found")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
