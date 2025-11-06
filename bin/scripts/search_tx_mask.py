#!/usr/bin/env python3
"""
TK11 TX Mask Search Tool
========================
Searches for potential TX mask locations in a .dat file.

This helps identify if the TX mask is stored in multiple locations
or if the offset is different than expected.

Usage:
    python search_tx_mask.py <file.dat>
"""

import sys
import os

def search_patterns(data):
    """Search for TX mask patterns"""

    patterns = [
        (0x03, "Original TX mask (USB disabled)"),
        (0x13, "Patched TX mask (USB enabled)"),
        (0x01, "FM only enabled"),
        (0x02, "AIR only enabled"),
        (0x04, "USB only enabled"),
        (0x11, "FM + WFM enabled"),
        (0x12, "AIR + WFM enabled"),
    ]

    print("="*80)
    print("SEARCHING FOR TX MASK PATTERNS")
    print("="*80)
    print()

    all_locations = {}

    for value, description in patterns:
        print(f"Searching for 0x{value:02X} ({description})...")
        locations = []

        for i in range(len(data)):
            if data[i] == value:
                locations.append(i)

        if locations:
            print(f"  Found {len(locations)} occurrences:")
            for loc in locations[:20]:  # Show first 20
                # Get context
                start = max(0, loc - 4)
                end = min(len(data), loc + 5)
                context = ' '.join(f'{data[j]:02X}' for j in range(start, end))
                if loc == 0x314D:
                    print(f"    0x{loc:04X} ({loc:6d}) ⭐ EXPECTED LOCATION! Context: {context}")
                else:
                    print(f"    0x{loc:04X} ({loc:6d})                       Context: {context}")

            if len(locations) > 20:
                print(f"    ... and {len(locations) - 20} more")

            all_locations[value] = locations
        else:
            print(f"  Not found")

        print()

    return all_locations

def analyze_offset(data, offset):
    """Analyze a specific offset"""

    if offset >= len(data):
        print(f"Offset 0x{offset:04X} is beyond file size!")
        return

    print("="*80)
    print(f"ANALYZING OFFSET 0x{offset:04X} ({offset} decimal)")
    print("="*80)
    print()

    value = data[offset]

    print(f"Value: 0x{value:02X} ({value} decimal)")
    print(f"Binary: {format(value, '08b')}")
    print()

    # Show 32 bytes of context
    start = max(0, offset - 16)
    end = min(len(data), offset + 17)

    print("Context (32 bytes around offset):")
    print(f"Offset: 0x{start:04X} - 0x{end-1:04X}")
    print()

    # Hex dump
    for i in range(start, end, 16):
        hex_line = f"0x{i:04X}:  "
        ascii_line = ""

        for j in range(i, min(i + 16, end)):
            if j == offset:
                hex_line += f"[{data[j]:02X}] "
                ascii_line += f"[{chr(data[j]) if 32 <= data[j] < 127 else '.'}]"
            else:
                hex_line += f"{data[j]:02X} "
                ascii_line += chr(data[j]) if 32 <= data[j] < 127 else '.'

        print(hex_line + "  " + ascii_line)

    print()
    print("[XX] = Target offset")

def find_candidates(data):
    """Find candidate locations that look like TX mask settings"""

    print("="*80)
    print("FINDING TX MASK CANDIDATES")
    print("="*80)
    print()
    print("Looking for bytes with specific bit patterns...")
    print()

    candidates = []

    # Look for bytes that have reasonable TX mask patterns
    # (combinations of bits 0, 1, 2, 4)
    for i in range(len(data)):
        value = data[i]

        # Check if value has bits only in positions 0,1,2,4
        # (bit 3 is usually not used)
        if value & 0xE8 == 0:  # Bits 3,5,6,7 should be 0
            if value != 0x00 and value != 0xFF:  # Not empty or full
                # This could be a TX mask
                candidates.append((i, value))

    print(f"Found {len(candidates)} potential TX mask locations")
    print()

    # Group by value
    by_value = {}
    for offset, value in candidates:
        if value not in by_value:
            by_value[value] = []
        by_value[value].append(offset)

    # Show most common values
    print("Most common candidate values:")
    sorted_values = sorted(by_value.items(), key=lambda x: len(x[1]), reverse=True)

    for value, offsets in sorted_values[:10]:
        print(f"  0x{value:02X}: {len(offsets)} occurrences")
        if 0x314D in offsets:
            print(f"       ⭐ Includes expected offset 0x314D!")

        # Show first few locations
        for offset in offsets[:5]:
            marker = " ⭐" if offset == 0x314D else ""
            print(f"       0x{offset:04X}{marker}")

        if len(offsets) > 5:
            print(f"       ... and {len(offsets) - 5} more")

    print()

def main():
    if len(sys.argv) < 2:
        print("TK11 TX Mask Search Tool")
        print()
        print("Usage:")
        print(f"  {sys.argv[0]} <file.dat>")
        print()
        print("This tool searches for TX mask patterns in the file")
        print("to help identify if the offset is correct or if there")
        print("are multiple locations where the TX mask is stored.")
        print()
        return 1

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return 1

    # Read file
    print(f"Reading: {file_path}")
    with open(file_path, 'rb') as f:
        data = f.read()

    print(f"Size: {len(data):,} bytes")
    print()

    # Search for patterns
    locations = search_patterns(data)

    # Analyze expected offset
    analyze_offset(data, 0x314D)

    # Find candidates
    find_candidates(data)

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()

    expected_offset = 0x314D
    if expected_offset < len(data):
        value_at_expected = data[expected_offset]
        print(f"Value at expected offset 0x{expected_offset:04X}: 0x{value_at_expected:02X}")

        if value_at_expected == 0x13:
            print("  ✅ This is the PATCHED value (USB TX enabled)")
        elif value_at_expected == 0x03:
            print("  ❌ This is the ORIGINAL value (USB TX disabled)")
            print("  → The patch was not applied or did not stick!")
        else:
            print(f"  ⚠️  Unexpected value!")
    else:
        print(f"ERROR: Expected offset 0x{expected_offset:04X} is beyond file size!")

    print()
    print("Next steps:")
    print("  1. Check if the value at 0x314D is 0x13 (patched)")
    print("  2. If not, re-apply the patch")
    print("  3. If yes, read from radio again and verify it stuck")
    print("  4. If it didn't stick, there may be another location")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
