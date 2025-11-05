#!/usr/bin/env python3
"""
Fix TK11 firmware header - recalculate checksum after patching

The firmware has a header with checksum/signature that must be updated
after modifying the firmware bytes.
"""

import struct
import hashlib
from pathlib import Path

def analyze_firmware_header(data):
    """Analyze firmware header structure"""

    print("="*80)
    print("FIRMWARE HEADER ANALYSIS")
    print("="*80)

    print(f"\nFirmware size: {len(data):,} bytes")

    # Common header locations
    header_sizes = [16, 32, 64, 128, 256, 512]

    for size in header_sizes:
        header = data[0:size]

        # Check if this looks like a header (high entropy, not encrypted)
        non_zero = sum(1 for b in header if b != 0x00 and b != 0xFF)
        density = non_zero / size

        print(f"\nFirst {size} bytes density: {density:.2%}")

        if size <= 64:
            print(f"Hex dump:")
            for i in range(0, size, 16):
                line = header[i:i+16]
                hex_str = ' '.join(f'{b:02x}' for b in line)
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
                print(f"  {i:04X}: {hex_str:<48} {ascii_str}")

def find_checksum_location(original_data, patched_data):
    """Find where checksum might be stored by comparing original and patched"""

    print("\n" + "="*80)
    print("FINDING CHECKSUM LOCATION")
    print("="*80)

    # Find all differences
    diffs = []
    for i in range(min(len(original_data), len(patched_data))):
        if original_data[i] != patched_data[i]:
            diffs.append(i)

    print(f"\nTotal bytes different: {len(diffs)}")

    if len(diffs) == 0:
        print("ERROR: Files are identical!")
        return None

    # Our patch location
    patch_offset = 0x0000314D

    print(f"\nKnown patch offset: 0x{patch_offset:08X}")
    print(f"Patch change: 0x{original_data[patch_offset]:02X} -> 0x{patched_data[patch_offset]:02X}")

    # Differences in first 512 bytes (likely header area)
    header_diffs = [d for d in diffs if d < 512]

    if header_diffs:
        print(f"\nWARNING: {len(header_diffs)} differences in first 512 bytes (header area)!")
        print("This might be a checksum field!")

        for diff in header_diffs[:20]:
            print(f"  0x{diff:04X}: 0x{original_data[diff]:02X} -> 0x{patched_data[diff]:02X}")
    else:
        print("\nNo differences in header area")

    # Look for checksum patterns in last 512 bytes
    tail_diffs = [d for d in diffs if d >= len(original_data) - 512]

    if tail_diffs:
        print(f"\n{len(tail_diffs)} differences in last 512 bytes (possible checksum area)!")

        for diff in tail_diffs[:20]:
            print(f"  0x{diff:08X}: 0x{original_data[diff]:02X} -> 0x{patched_data[diff]:02X}")

def calculate_checksums(data):
    """Calculate various checksums of firmware"""

    print("\n" + "="*80)
    print("CHECKSUM CALCULATIONS")
    print("="*80)

    # Simple sum
    simple_sum = sum(data) & 0xFFFFFFFF
    print(f"\nSimple sum (32-bit): 0x{simple_sum:08X}")

    # CRC32
    import zlib
    crc32 = zlib.crc32(data) & 0xFFFFFFFF
    print(f"CRC32: 0x{crc32:08X}")

    # MD5
    md5 = hashlib.md5(data).hexdigest()
    print(f"MD5: {md5}")

    # SHA256
    sha256 = hashlib.sha256(data).hexdigest()
    print(f"SHA256: {sha256[:32]}...")

    # Checksum of body (excluding header)
    for header_size in [16, 32, 64, 128, 256]:
        body = data[header_size:]
        body_sum = sum(body) & 0xFFFFFFFF
        body_crc = zlib.crc32(body) & 0xFFFFFFFF

        print(f"\nExcluding first {header_size} bytes:")
        print(f"  Sum: 0x{body_sum:08X}")
        print(f"  CRC32: 0x{body_crc:08X}")

def try_fix_checksum(data, checksum_offset, checksum_type='crc32'):
    """Try to fix checksum at given offset"""

    print("\n" + "="*80)
    print(f"ATTEMPTING CHECKSUM FIX at 0x{checksum_offset:08X}")
    print("="*80)

    # Zero out the checksum field first
    data_copy = bytearray(data)
    data_copy[checksum_offset:checksum_offset+4] = b'\x00\x00\x00\x00'

    # Calculate new checksum
    import zlib

    if checksum_type == 'crc32':
        new_checksum = zlib.crc32(data_copy) & 0xFFFFFFFF
    elif checksum_type == 'sum':
        new_checksum = sum(data_copy) & 0xFFFFFFFF
    else:
        print(f"Unknown checksum type: {checksum_type}")
        return data

    print(f"Calculated {checksum_type}: 0x{new_checksum:08X}")

    # Write new checksum (little-endian)
    data_copy[checksum_offset:checksum_offset+4] = struct.pack('<I', new_checksum)

    print(f"Updated bytes at 0x{checksum_offset:08X}: {data_copy[checksum_offset:checksum_offset+4].hex(' ')}")

    return bytes(data_copy)

def create_fixed_firmware(original_path, patched_path, output_path):
    """Create firmware with fixed checksum"""

    print("="*80)
    print("FIRMWARE HEADER FIX TOOL")
    print("="*80)

    with open(original_path, 'rb') as f:
        original_data = f.read()

    with open(patched_path, 'rb') as f:
        patched_data = bytearray(f.read())

    print(f"\nOriginal: {len(original_data):,} bytes")
    print(f"Patched: {len(patched_data):,} bytes")

    # Analyze header
    print("\n" + "="*80)
    print("ORIGINAL FIRMWARE HEADER")
    analyze_firmware_header(original_data)

    print("\n" + "="*80)
    print("PATCHED FIRMWARE HEADER")
    analyze_firmware_header(patched_data)

    # Find differences
    find_checksum_location(original_data, patched_data)

    # Calculate checksums
    print("\n" + "="*80)
    print("ORIGINAL FIRMWARE CHECKSUMS")
    calculate_checksums(original_data)

    print("\n" + "="*80)
    print("PATCHED FIRMWARE CHECKSUMS")
    calculate_checksums(patched_data)

    # Common checksum locations to try
    checksum_locations = [
        0x0C,  # Offset 12 (common)
        0x10,  # Offset 16
        0x1C,  # Offset 28
        0x20,  # Offset 32
        0x3C,  # Offset 60
        0x40,  # Offset 64
    ]

    print("\n" + "="*80)
    print("TRYING COMMON CHECKSUM LOCATIONS")
    print("="*80)

    # Extract potential checksum from original
    print("\nOriginal firmware values at common checksum locations:")
    for loc in checksum_locations:
        val = struct.unpack('<I', original_data[loc:loc+4])[0]
        print(f"  0x{loc:04X}: 0x{val:08X}")

    # Try to fix with different methods
    fixed_versions = []

    for loc in checksum_locations:
        for chk_type in ['crc32', 'sum']:
            fixed = try_fix_checksum(patched_data, loc, chk_type)

            output_name = output_path.parent / f"{output_path.stem}_FIX_{loc:04X}_{chk_type}{output_path.suffix}"

            with open(output_name, 'wb') as f:
                f.write(fixed)

            fixed_versions.append({
                'file': output_name,
                'offset': loc,
                'type': chk_type
            })

            print(f"\nCreated: {output_name.name}")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nCreated {len(fixed_versions)} test versions with different checksum fixes")
    print("\nTry loading each one into TK11.exe:")

    for i, ver in enumerate(fixed_versions, 1):
        print(f"\n{i}. {ver['file'].name}")
        print(f"   Checksum at: 0x{ver['offset']:04X}")
        print(f"   Type: {ver['type']}")

    print("\nOne of these should work!")
    print("If none work, the checksum algorithm is more complex.")

def main():
    base_path = Path(r"E:\AI\tk11")

    original_fw = base_path / "TK11_v5.00.09_ENG.bin"
    patched_fw = base_path / "patched_firmware" / "TK11_PATCHED_USB_TX_ENABLE_20251029_154257.bin"
    output_fw = base_path / "patched_firmware" / "TK11_PATCHED_USB_FIXED.bin"

    if not original_fw.exists():
        print(f"ERROR: Original firmware not found: {original_fw}")
        return

    if not patched_fw.exists():
        print(f"ERROR: Patched firmware not found: {patched_fw}")
        return

    create_fixed_firmware(original_fw, patched_fw, output_fw)

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. Try loading each _FIX_*.bin file into TK11.exe
2. One of them should NOT give "File version is Wrong"
3. If found, flash that version to the radio
4. Test the hybrid mode!

If none work:
  - Checksum algorithm is more complex
  - May need to reverse engineer TK11.exe
  - Or use alternative approach (AM mode)
""")

if __name__ == "__main__":
    main()
