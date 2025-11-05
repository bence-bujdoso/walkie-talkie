#!/usr/bin/env python3
"""
Deep analysis of mode-related regions in TK11 firmware
Focus on CW, USB, LSB detection and mode control structures
"""

import struct
import re

def analyze_region(data, offset, size=256):
    """Analyze a region around a given offset"""
    start = max(0, offset - 128)
    end = min(len(data), offset + 128)
    region = data[start:end]

    print(f"\n{'='*80}")
    print(f"REGION ANALYSIS @ 0x{offset:08X}")
    print(f"{'='*80}")

    # Hex dump
    print("\nHEX DUMP:")
    for i in range(0, len(region), 16):
        chunk = region[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        addr = start + i
        print(f"0x{addr:08X}:  {hex_str:<48}  {ascii_str}")

    # Look for mode strings nearby
    print("\n\nNEARBY ASCII STRINGS:")
    pattern = rb'[\x20-\x7E]{3,}'
    nearby_start = max(0, offset - 512)
    nearby_end = min(len(data), offset + 512)
    nearby_data = data[nearby_start:nearby_end]

    for match in re.finditer(pattern, nearby_data):
        str_offset = nearby_start + match.start()
        string = match.group().decode('ascii', errors='ignore')
        distance = str_offset - offset
        print(f"  0x{str_offset:08X} ({distance:+5d}): {string}")

def search_mode_sequences(data):
    """Search for mode enumeration sequences"""
    print("\n" + "="*80)
    print("SEARCHING FOR MODE ENUMERATION PATTERNS")
    print("="*80)

    # Look for common mode sequences
    # Pattern: strings appearing close together suggesting menu/mode lists
    mode_keywords = [b'FM', b'AM', b'USB', b'LSB', b'CW', b'WFM', b'NFM', b'SSB']

    print("\nSearching for clustered mode keywords...")

    # Find all keyword positions
    positions = {}
    for keyword in mode_keywords:
        offset = 0
        positions[keyword] = []
        while True:
            pos = data.find(keyword, offset)
            if pos == -1:
                break
            positions[keyword].append(pos)
            offset = pos + 1

    # Find clusters (multiple mode keywords within 1KB)
    print("\n*** MODE KEYWORD CLUSTERS ***")
    all_positions = []
    for kw, pos_list in positions.items():
        for pos in pos_list:
            all_positions.append((pos, kw))

    all_positions.sort()

    clusters = []
    i = 0
    while i < len(all_positions):
        cluster = [all_positions[i]]
        j = i + 1
        while j < len(all_positions) and all_positions[j][0] - all_positions[i][0] < 1024:
            cluster.append(all_positions[j])
            j += 1
        if len(cluster) >= 2:  # At least 2 mode keywords close together
            clusters.append(cluster)
            i = j
        else:
            i += 1

    for idx, cluster in enumerate(clusters):
        print(f"\nCluster {idx+1}:")
        for pos, kw in cluster:
            print(f"  0x{pos:08X}: {kw.decode('ascii')}")

    return clusters

def search_usb_lsb_patterns(data):
    """Specifically search for USB/LSB references"""
    print("\n" + "="*80)
    print("SEARCHING FOR USB/LSB/SSB PATTERNS")
    print("="*80)

    patterns = {
        'USB (upper case)': b'USB',
        'usb (lower case)': b'usb',
        'LSB (upper case)': b'LSB',
        'lsb (lower case)': b'lsb',
        'SSB (upper case)': b'SSB',
        'ssb (lower case)': b'ssb',
        'U.S.B (dots)': b'U.S.B',
        'L.S.B (dots)': b'L.S.B',
    }

    results = {}
    for name, pattern in patterns.items():
        positions = []
        offset = 0
        while True:
            pos = data.find(pattern, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1
        results[name] = positions
        if positions:
            print(f"\n[FOUND] {name}: {len(positions)} occurrence(s)")
            for pos in positions[:10]:  # Show first 10
                print(f"  @ 0x{pos:08X}")

    return results

def analyze_cw_regions(data, cw_offsets):
    """Deep dive into CW-related regions"""
    print("\n" + "="*80)
    print("DEEP ANALYSIS OF CW REGIONS")
    print("="*80)

    for offset in cw_offsets:
        analyze_region(data, offset)

def search_mode_table_structures(data):
    """Look for mode configuration table structures"""
    print("\n" + "="*80)
    print("SEARCHING FOR MODE CONFIGURATION TABLES")
    print("="*80)

    # Look for repeating structures that might be mode definitions
    # Common structure: mode_id, flags, name_offset, handler_offset

    print("\nSearching for repeating 8-byte structures...")

    candidates = []
    for i in range(0, len(data) - 64, 4):
        # Look for 4+ consecutive structures with similar patterns
        structures = []
        for j in range(8):
            offset = i + (j * 8)
            if offset + 8 > len(data):
                break
            struct_data = data[offset:offset+8]
            structures.append(struct_data)

        # Check if they look like a table (some regularity)
        if len(structures) >= 4:
            # Check for patterns
            first_bytes = [s[0] for s in structures if len(s) > 0]
            if len(set(first_bytes)) >= 3 and all(b < 32 for b in first_bytes[:4]):
                candidates.append((i, structures[:5]))

    print(f"\nFound {len(candidates)} potential mode table candidates")
    print("\nTop 20 candidates:")
    for idx, (offset, structs) in enumerate(candidates[:20]):
        print(f"\n  Candidate {idx+1} @ 0x{offset:08X}:")
        for j, s in enumerate(structs):
            hex_str = ' '.join(f'{b:02x}' for b in s)
            print(f"    [{j}] {hex_str}")

def analyze_flag_bytes(data):
    """Look for configuration flag bytes"""
    print("\n" + "="*80)
    print("ANALYZING POTENTIAL MODE FLAG BYTES")
    print("="*80)

    # Look for sequences that might be mode enable/disable flags
    # Pattern: byte masks like 0x1F (5 modes), 0x07 (3 modes), etc.

    interesting_flag_values = [
        0x03,  # 2 modes (FM, AM)
        0x07,  # 3 modes
        0x0F,  # 4 modes
        0x1F,  # 5 modes (FM, AM, USB, LSB, CW)
        0x3F,  # 6 modes
    ]

    print("\nSearching for mode flag bytes...")
    for flag_val in interesting_flag_values:
        positions = []
        for i in range(len(data)):
            if data[i] == flag_val:
                # Check if surrounded by interesting values
                if i > 4 and i < len(data) - 4:
                    context = data[i-4:i+5]
                    # Look for patterns that suggest configuration
                    if any(b in [0x00, 0x01, 0xFF] for b in context):
                        positions.append(i)

        if positions:
            print(f"\n  Flag value 0x{flag_val:02X} ({bin(flag_val)}): {len(positions)} occurrences")
            print(f"    Showing first 10:")
            for pos in positions[:10]:
                context = data[max(0,pos-8):min(len(data),pos+9)]
                hex_str = ' '.join(f'{b:02x}' for b in context)
                print(f"      0x{pos:08X}: {hex_str}")

def main():
    print("="*80)
    print("TK11 FIRMWARE - DEEP MODE ANALYSIS")
    print("="*80)

    # Load firmware
    with open('E:\\AI\\tk11\\TK11_v5.00.09_ENG.bin', 'rb') as f:
        data = f.read()

    print(f"\nFirmware size: {len(data)} bytes\n")

    # Known CW offsets from first scan
    cw_offsets = [0x0002E0E0, 0x0002EA5E, 0x00036F84, 0x00037C74, 0x0003CB67]

    # 1. Search for USB/LSB/SSB
    usb_lsb_results = search_usb_lsb_patterns(data)

    # 2. Find mode clusters
    clusters = search_mode_sequences(data)

    # 3. Analyze CW regions
    print("\n\n" + "="*80)
    print("ANALYZING FIRST 2 CW REFERENCE REGIONS")
    print("="*80)
    for offset in cw_offsets[:2]:
        analyze_region(data, offset, 256)

    # 4. Look for mode tables
    search_mode_table_structures(data)

    # 5. Analyze flag bytes
    analyze_flag_bytes(data)

    print("\n\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
