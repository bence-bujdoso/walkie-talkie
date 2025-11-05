#!/usr/bin/env python3
"""
Compare all existing firmware files to find the validation pattern
"""

from pathlib import Path
import struct

def analyze_file(filepath):
    """Analyze all potential checksum locations in a firmware file"""

    with open(filepath, 'rb') as f:
        data = f.read()

    info = {
        'name': filepath.name,
        'size': len(data),
        'tx_byte': data[0x314D] if len(data) > 0x314D else None,
        'last_4_bytes': struct.unpack('<I', data[-4:])[0] if len(data) >= 4 else None,
        'last_4_be': struct.unpack('>I', data[-4:])[0] if len(data) >= 4 else None,
        'first_4_bytes': struct.unpack('<I', data[:4])[0] if len(data) >= 4 else None,
        'header_0x00': struct.unpack('<I', data[0x00:0x04])[0] if len(data) >= 0x04 else None,
        'header_0x04': struct.unpack('<I', data[0x04:0x08])[0] if len(data) >= 0x08 else None,
        'header_0x08': struct.unpack('<I', data[0x08:0x0C])[0] if len(data) >= 0x0C else None,
        'header_0x0C': struct.unpack('<I', data[0x0C:0x10])[0] if len(data) >= 0x10 else None,
        'header_0x10': struct.unpack('<I', data[0x10:0x14])[0] if len(data) >= 0x14 else None,
        'header_0x14': struct.unpack('<I', data[0x14:0x18])[0] if len(data) >= 0x18 else None,
        'header_0x18': struct.unpack('<I', data[0x18:0x1C])[0] if len(data) >= 0x1C else None,
        'header_0x1C': struct.unpack('<I', data[0x1C:0x20])[0] if len(data) >= 0x20 else None,
        'sum_all': sum(data) & 0xFFFFFFFF,
        'sum_minus_4': sum(data[:-4]) & 0xFFFFFFFF if len(data) > 4 else None,
        'sum_minus_8': sum(data[:-8]) & 0xFFFFFFFF if len(data) > 8 else None,
        'sum_from_0x100': sum(data[0x100:]) & 0xFFFFFFFF if len(data) > 0x100 else None,
        'sum_from_0x20': sum(data[0x20:]) & 0xFFFFFFFF if len(data) > 0x20 else None,
    }

    return info

def main():
    print("="*80)
    print("COMPARING ALL FIRMWARE FILES")
    print("="*80)

    # Files to analyze
    files = [
        Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin"),
        Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin"),
        Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin"),
        Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLE_20251029_154257.bin"),
        Path(r"E:\AI\tk11\patched_firmware\TK11_PATCHED_All_Modes_20251029_152304.bin"),
    ]

    # Analyze all files
    results = []
    for filepath in files:
        if filepath.exists():
            print(f"\nAnalyzing: {filepath.name}")
            info = analyze_file(filepath)
            results.append(info)
        else:
            print(f"\nSkipping (not found): {filepath.name}")

    # Print comparison table
    print("\n" + "="*80)
    print("COMPARISON TABLE")
    print("="*80)

    # TX Byte comparison
    print("\n[TX BYTE at 0x314D]")
    print("-" * 80)
    for r in results:
        tx_status = "USB ENABLED" if r['tx_byte'] == 0x13 else "USB DISABLED"
        print(f"{r['name']:<50} 0x{r['tx_byte']:02X} ({tx_status})")

    # Last 4 bytes comparison
    print("\n[LAST 4 BYTES - Potential Checksum]")
    print("-" * 80)
    for r in results:
        match = "MATCH" if r['last_4_bytes'] == r['sum_minus_4'] else "MISMATCH"
        print(f"{r['name']:<50}")
        print(f"  Stored: 0x{r['last_4_bytes']:08X}  |  Sum(all-4): 0x{r['sum_minus_4']:08X}  [{match}]")

    # Header fields comparison
    print("\n[HEADER FIELDS - Looking for differences]")
    print("-" * 80)

    header_fields = [
        ('header_0x00', '0x00'),
        ('header_0x04', '0x04'),
        ('header_0x08', '0x08'),
        ('header_0x0C', '0x0C'),
        ('header_0x10', '0x10'),
        ('header_0x14', '0x14'),
        ('header_0x18', '0x18'),
        ('header_0x1C', '0x1C'),
    ]

    for field, offset in header_fields:
        values = [r[field] for r in results]
        if len(set(values)) > 1:  # Only show if there are differences
            print(f"\nOffset {offset} - DIFFERENCES FOUND:")
            for r in results:
                print(f"  {r['name']:<50} 0x{r[field]:08X}")
        else:
            print(f"Offset {offset}: All match (0x{values[0]:08X})")

    # Check for patterns
    print("\n" + "="*80)
    print("LOOKING FOR VALIDATION PATTERNS")
    print("="*80)

    # Compare original vs our patched
    if len(results) >= 2:
        orig = results[0]
        our_patch = results[1]

        print("\nComparing ORIGINAL vs OUR_PATCHED_CHECKSUM_FIXED:")
        print("-" * 80)

        # Check each header field
        for field, offset in header_fields:
            if orig[field] != our_patch[field]:
                print(f"DIFF at {offset}: 0x{orig[field]:08X} -> 0x{our_patch[field]:08X}")

        # Check if any header field matches a calculated checksum
        print("\n[SEARCHING FOR CHECKSUM MATCHES IN HEADER]")
        print("-" * 80)

        checksums_to_test = [
            ('sum_minus_4', 'Sum (all bytes - 4)'),
            ('sum_minus_8', 'Sum (all bytes - 8)'),
            ('sum_from_0x100', 'Sum (from 0x100)'),
            ('sum_from_0x20', 'Sum (from 0x20)'),
        ]

        for checksum_field, desc in checksums_to_test:
            orig_checksum = orig[checksum_field]

            # Check if this checksum appears in any header field
            for field, offset in header_fields:
                if orig[field] == orig_checksum:
                    print(f"*** MATCH: Header {offset} == {desc} (0x{orig_checksum:08X}) ***")

                    # Check our patched version
                    our_checksum = our_patch[checksum_field]
                    our_header = our_patch[field]

                    if our_header == our_checksum:
                        print(f"    Our patch: CORRECT (0x{our_checksum:08X})")
                    else:
                        print(f"    Our patch: INCORRECT!")
                        print(f"      Header has: 0x{our_header:08X}")
                        print(f"      Should be:  0x{our_checksum:08X}")
                        print(f"      ACTION: Need to update header {offset} to 0x{our_checksum:08X}")

if __name__ == "__main__":
    main()
