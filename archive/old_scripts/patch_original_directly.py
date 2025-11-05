#!/usr/bin/env python3
"""
Patch original firmware at exact offset - minimal changes
Alternative approach: modify ORIGINAL file directly with CRC16 fix
"""

from pathlib import Path
import struct
import zlib

def calculate_crc16_xmodem(data):
    """CRC16-XMODEM - common in embedded firmware"""
    crc = 0
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def calculate_crc16_ccitt(data):
    """CRC16-CCITT"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc

def calculate_crc16_modbus(data):
    """CRC16-MODBUS"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def patch_firmware():
    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    output_dir = Path(r"E:\AI\tk11\patched_firmware")
    output_dir.mkdir(exist_ok=True)

    print("="*80)
    print("TK11 FIRMWARE PATCHER - MINIMAL MODIFICATION + CRC16 FIX")
    print("="*80)

    # Read original
    with open(original, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nOriginal firmware: {original}")
    print(f"Size: {len(data):,} bytes")

    # Show original header
    print("\nOriginal header (first 32 bytes):")
    for i in range(0, 32, 16):
        hex_str = ' '.join(f'{data[j]:02x}' for j in range(i, i+16))
        print(f"  0x{i:04X}: {hex_str}")

    # ONLY patch the TX validation mask
    offset = 0x0000314D
    original_value = data[offset]
    new_value = 0x13  # Enable USB mode (bit 4)

    print(f"\n{'='*80}")
    print("PATCH APPLICATION")
    print("="*80)
    print(f"Patch location: 0x{offset:08X}")
    print(f"Original value: 0x{original_value:02X} (binary: {original_value:08b})")
    print(f"New value:      0x{new_value:02X} (binary: {new_value:08b})")

    if original_value != 0x03:
        print(f"\n⚠️  WARNING: Expected 0x03, found 0x{original_value:02X}")
        print("This may not be the correct offset!")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return

    # Apply single byte patch
    data[offset] = new_value
    print(f"\n✓ Patch applied at 0x{offset:08X}")

    # Try multiple CRC16 algorithms and locations
    print(f"\n{'='*80}")
    print("CRC16 CALCULATION AND UPDATE")
    print("="*80)

    # Potential CRC locations in header (based on common firmware structures)
    crc_candidates = [
        # (offset, description, data_start)
        (0x02, "Header+2 (skip signature)", 0x04),
        (0x04, "Header+4 (after length?)", 0x06),
        (0x06, "Header+6", 0x08),
        (0x0A, "Header+10", 0x0C),
        (0x0E, "Header+14", 0x10),
        (0x12, "Header+18", 0x14),
    ]

    # Create multiple versions with different CRC algorithms
    algorithms = [
        ('XMODEM', calculate_crc16_xmodem),
        ('CCITT', calculate_crc16_ccitt),
        ('MODBUS', calculate_crc16_modbus),
    ]

    versions_created = []

    for algo_name, algo_func in algorithms:
        for crc_offset, desc, data_start in crc_candidates:
            # Create a copy for this version
            version_data = bytearray(data)

            # Calculate CRC over data AFTER the CRC field to EOF
            crc_data = version_data[data_start:]
            crc16 = algo_func(crc_data)

            # Store in little-endian
            version_data[crc_offset:crc_offset+2] = struct.pack('<H', crc16)

            # Create filename
            output_name = f"TK11_PATCHED_CRC16_{algo_name}_offset_{crc_offset:04X}.bin"
            output_path = output_dir / output_name

            # Write output
            with open(output_path, 'wb') as f:
                f.write(version_data)

            versions_created.append({
                'file': output_name,
                'algorithm': algo_name,
                'crc_offset': crc_offset,
                'crc_value': crc16,
                'description': desc
            })

            print(f"✓ Created: {output_name}")
            print(f"  Algorithm: CRC16-{algo_name}")
            print(f"  CRC location: 0x{crc_offset:04X} ({desc})")
            print(f"  CRC value: 0x{crc16:04X}")
            print(f"  Data range: 0x{data_start:04X} to EOF")
            print()

    # Also create version with NO CRC change (just the patch)
    output_name = "TK11_PATCHED_NO_CRC_FIX.bin"
    output_path = output_dir / output_name
    with open(output_path, 'wb') as f:
        f.write(data)
    print(f"✓ Created: {output_name} (patch only, no CRC fix)")

    print(f"\n{'='*80}")
    print("SUMMARY")
    print("="*80)
    print(f"\nCreated {len(versions_created) + 1} firmware versions:")
    print(f"  - {len(versions_created)} with different CRC16 fixes")
    print(f"  - 1 with patch only (no CRC fix)")
    print(f"\nAll files saved to: {output_dir}")

    print(f"\n{'='*80}")
    print("TESTING STRATEGY")
    print("="*80)
    print("""
1. First, use the PATCHED TK11.exe from Solution 1
   - This bypasses TK11.exe validation
   - Test with: TK11_PATCHED_NO_CRC_FIX.bin
   - If flash succeeds → radio bootloader doesn't validate CRC!

2. If that works, you're done! No CRC fix needed.

3. If flash FAILS with bootloader error:
   - Radio bootloader IS validating CRC
   - Try each CRC16 version one by one:
     a) Start with XMODEM variants (most common)
     b) Then CCITT variants
     c) Finally MODBUS variants

4. Test procedure for each:
   - Load firmware in TK11_PATCHED_BYPASS.exe
   - Try to flash to radio
   - If bootloader accepts it → SUCCESS!
   - If not, try next version

5. Keep track of which one works for future patches!

IMPORTANT: Test with DUMMY LOAD connected, not antenna!
""")

    print(f"\n{'='*80}")
    print("FILES CREATED")
    print("="*80)
    for v in versions_created[:10]:  # Show first 10
        print(f"  {v['file']}")
    if len(versions_created) > 10:
        print(f"  ... and {len(versions_created) - 10} more")

    print(f"\n✓ Patch complete!")

if __name__ == "__main__":
    patch_firmware()
