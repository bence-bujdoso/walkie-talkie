#!/usr/bin/env python3
"""
TK11 Firmware Patcher - Enable DSB Mode TX

WARNING: This script modifies firmware binary!
- Can brick your radio if done incorrectly
- Voids warranty
- Use at your own risk
- ALWAYS keep backup of original firmware
"""

import struct
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

# Top candidate offsets from find_tx_mask.py analysis
TOP_CANDIDATES = [
    0x0000314D,  # Score: 21 (highest)
    0x0000338C,  # Score: 21
    0x000041EC,  # Score: 21
    0x00035FE4,  # Score: 21
    0x0003B691,  # Score: 21
    0x0003E520,  # Score: 21
    0x0004DFF6,  # Score: 21
    0x000565A2,  # Score: 21
    0x000086F4,  # Score: 20
    0x000268AD,  # Score: 20
]

# Patch values to test
PATCH_VALUES = {
    0x23: "Enable Mode 0x05 (DSB hypothesis 1)",
    0x2F: "Enable Modes 0x05, 0x06, 0x07, 0x08 (all DSB tests)",
    0x3F: "Enable Modes 0x00-0x05 (FM/AM/USB/LSB/DSB)",
    0x7F: "Enable Modes 0x00-0x06 (extended)",
    0xFF: "Enable ALL modes (full unlock - RISKY)",
}

def calculate_checksum(data):
    """Calculate SHA256 checksum for verification"""
    return hashlib.sha256(data).hexdigest()

def verify_firmware(filepath):
    """Verify firmware file integrity"""

    expected_size = 357976  # From analysis

    with open(filepath, 'rb') as f:
        data = f.read()

    size_ok = len(data) == expected_size
    checksum = calculate_checksum(data)

    return {
        'size': len(data),
        'size_ok': size_ok,
        'checksum': checksum
    }

def patch_firmware(input_path, output_path, offset, new_value, description):
    """
    Patch firmware at specific offset

    Args:
        input_path: Original firmware file
        output_path: Output patched firmware
        offset: Byte offset to patch
        new_value: New byte value
        description: Description of patch

    Returns:
        dict with patch results
    """

    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    original_value = data[offset]

    # Only patch if original is 0x03
    if original_value != 0x03:
        return {
            'success': False,
            'reason': f'Expected 0x03 at offset, found 0x{original_value:02X}',
            'offset': offset,
            'original': original_value,
            'new': new_value
        }

    # Apply patch
    data[offset] = new_value

    # Write output
    with open(output_path, 'wb') as f:
        f.write(data)

    # Verify
    with open(output_path, 'rb') as f:
        verify_data = f.read()

    if verify_data[offset] != new_value:
        return {
            'success': False,
            'reason': 'Verification failed - byte not changed',
            'offset': offset
        }

    return {
        'success': True,
        'offset': offset,
        'original': original_value,
        'new': new_value,
        'description': description,
        'size': len(verify_data),
        'checksum': calculate_checksum(verify_data)
    }

def create_test_matrix(input_path, output_dir):
    """
    Create test matrix: multiple offsets x multiple patch values
    Only patches offsets where byte is currently 0x03
    """

    print("="*80)
    print("TK11 FIRMWARE PATCHER - DSB MODE ENABLE")
    print("="*80)
    print("\nWARNING: This will create multiple patched firmware versions!")
    print("Only offsets containing 0x03 will be patched.")
    print("\n" + "="*80)

    # Verify input
    print(f"\nVerifying input firmware: {input_path}")
    verify = verify_firmware(input_path)

    print(f"  Size: {verify['size']:,} bytes - {'OK' if verify['size_ok'] else 'UNEXPECTED'}")
    print(f"  SHA256: {verify['checksum'][:16]}...")

    if not verify['size_ok']:
        print("\n⚠️  WARNING: Firmware size doesn't match expected value!")
        print("    Expected: 357,976 bytes")
        print(f"    Found: {verify['size']:,} bytes")
        response = input("\nContinue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup
    backup_name = f"TK11_v5.00.09_ENG_ORIGINAL_{timestamp}.bin"
    backup_path = output_dir / backup_name
    shutil.copy2(input_path, backup_path)
    print(f"\n[OK] Backup created: {backup_name}")

    # Read original firmware
    with open(input_path, 'rb') as f:
        original_data = f.read()

    # Find which offsets actually have 0x03
    valid_offsets = []

    print(f"\n--- SCANNING CANDIDATE OFFSETS ---")
    for offset in TOP_CANDIDATES:
        value = original_data[offset]
        status = "[OK] 0x03 FOUND" if value == 0x03 else f"[X] Has 0x{value:02X}"
        print(f"  0x{offset:08X}: {status}")

        if value == 0x03:
            valid_offsets.append(offset)

    if not valid_offsets:
        print("\n[ERROR] ERROR: No valid offsets found!")
        print("   All candidate offsets have non-0x03 values.")
        print("   This means the TX mask is elsewhere, or firmware is different.")
        return

    print(f"\n[OK] Found {len(valid_offsets)} valid offsets to patch")

    # Generate patches
    print(f"\n--- GENERATING PATCHED FIRMWARE VERSIONS ---")
    print(f"Creating {len(valid_offsets)} offsets x {len(PATCH_VALUES)} values = {len(valid_offsets) * len(PATCH_VALUES)} files\n")

    results = []
    success_count = 0

    for offset_idx, offset in enumerate(valid_offsets, 1):
        for value_idx, (patch_value, description) in enumerate(PATCH_VALUES.items(), 1):

            output_name = f"TK11_PATCHED_OFF{offset:08X}_VAL{patch_value:02X}_{timestamp}.bin"
            output_path = output_dir / output_name

            result = patch_firmware(
                input_path,
                output_path,
                offset,
                patch_value,
                description
            )

            result['output_file'] = output_name
            result['offset_idx'] = offset_idx
            result['value_idx'] = value_idx

            results.append(result)

            if result['success']:
                success_count += 1
                status = "[OK]"
            else:
                status = "[X]"

            print(f"  [{offset_idx}/{len(valid_offsets)}] "
                  f"[{value_idx}/{len(PATCH_VALUES)}] "
                  f"{status} Offset 0x{offset:08X} → 0x{patch_value:02X}")

    # Summary
    print("\n" + "="*80)
    print("PATCHING COMPLETE")
    print("="*80)
    print(f"\nSuccess: {success_count}/{len(results)} files created")
    print(f"Output directory: {output_dir}")

    # Create index file
    index_path = output_dir / f"PATCH_INDEX_{timestamp}.txt"

    with open(index_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("TK11 FIRMWARE PATCH INDEX\n")
        f.write("="*80 + "\n")
        f.write(f"\nTimestamp: {timestamp}\n")
        f.write(f"Original firmware: {input_path}\n")
        f.write(f"Original checksum: {verify['checksum']}\n")
        f.write(f"\nTotal patches: {len(results)}\n")
        f.write(f"Successful: {success_count}\n")
        f.write("\n" + "="*80 + "\n")
        f.write("PATCHED FILES\n")
        f.write("="*80 + "\n\n")

        for result in results:
            if result['success']:
                f.write(f"File: {result['output_file']}\n")
                f.write(f"  Offset: 0x{result['offset']:08X}\n")
                f.write(f"  Change: 0x{result['original']:02X} → 0x{result['new']:02X}\n")
                f.write(f"  Description: {result['description']}\n")
                f.write(f"  Checksum: {result['checksum'][:16]}...\n")
                f.write("\n")

    print(f"\n[OK] Index file created: {index_path.name}")

    return results, timestamp

def create_recommended_patches(input_path, output_dir):
    """
    Create only the most likely patches for easier testing
    """

    print("="*80)
    print("CREATING RECOMMENDED PATCHES (Conservative Approach)")
    print("="*80)

    # Read firmware
    with open(input_path, 'rb') as f:
        data = f.read()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Backup
    backup_path = output_dir / f"TK11_ORIGINAL_{timestamp}.bin"
    shutil.copy2(input_path, backup_path)
    print(f"\n[OK] Backup: {backup_path.name}")

    # Find first valid offset
    valid_offset = None
    for offset in TOP_CANDIDATES:
        if data[offset] == 0x03:
            valid_offset = offset
            break

    if not valid_offset:
        print("\n[ERROR] No valid offset found with 0x03 value")
        return

    print(f"\n[OK] Using offset: 0x{valid_offset:08X}")

    # Create 3 recommended patches
    recommended = [
        (0x23, "Mode_05_DSB", "Enable mode 0x05 only (safest)"),
        (0x2F, "Modes_05-08_DSB", "Enable DSB test modes 0x05-0x08"),
        (0xFF, "All_Modes", "Enable all modes (full unlock - testing only)"),
    ]

    print(f"\nCreating 3 recommended patches...")

    for patch_val, suffix, desc in recommended:
        output_name = f"TK11_PATCHED_{suffix}_{timestamp}.bin"
        output_path = output_dir / output_name

        result = patch_firmware(input_path, output_path, valid_offset, patch_val, desc)

        if result['success']:
            print(f"  [OK] {output_name}")
            print(f"      {desc}")
        else:
            print(f"  [X] Failed: {result['reason']}")

    print(f"\n" + "="*80)
    print("READY FOR TESTING")
    print("="*80)
    print(f"""
Start with: TK11_PATCHED_Mode_05_DSB_{timestamp}.bin

This enables ONLY mode 0x05 (DSB hypothesis 1) - the safest option.

If mode 0x05 doesn't work, try the next file.
""")

def main():
    print("="*80)
    print("TK11 FIRMWARE PATCHER")
    print("="*80)
    print("""
This tool patches the TK11 firmware to enable DSB mode transmission.

*** WARNING - READ CAREFULLY ***

RISKS:
- Can BRICK your radio if firmware is corrupted
- VOIDS WARRANTY
- May violate regulatory compliance
- Could damage radio if used incorrectly

REQUIREMENTS:
- Backup of original firmware
- Firmware flashing tool/software
- Understanding of firmware update procedure
- Willingness to accept risks

DISCLAIMER:
- Use at your own risk
- No guarantee of success
- Author not responsible for damage
""")

    response = input("\nDo you understand and accept the risks? (type 'I ACCEPT'): ")

    if response != "I ACCEPT":
        print("\nAborted. Risks not accepted.")
        return

    print("\n" + "="*80)
    print("PATCH MODE")
    print("="*80)
    print("""
1. Create ALL test patches (10 offsets x 5 values = 50 files)
   - For comprehensive testing
   - Takes more time
   - More files to test

2. Create RECOMMENDED patches only (3 files)
   - Fastest option
   - Uses most likely offset
   - 3 patch levels to test

3. EXIT
""")

    choice = input("Select mode (1/2/3) [default: 2]: ").strip() or "2"

    if choice == "3":
        print("\nExiting.")
        return

    input_path = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    output_dir = Path(r"E:\AI\tk11\patched_firmware")

    if not input_path.exists():
        print(f"\n[ERROR] ERROR: Firmware not found: {input_path}")
        return

    if choice == "1":
        create_test_matrix(input_path, output_dir)
    elif choice == "2":
        create_recommended_patches(input_path, output_dir)

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. Review the patched firmware files in: patched_firmware/

2. Choose ONE patched firmware to test:
   - Start with Mode_05_DSB (safest)
   - If that doesn't work, try Modes_05-08_DSB
   - Full unlock (All_Modes) is for advanced testing only

3. Flash firmware to radio using TK11 programming software
   - Consult radio manual for firmware update procedure
   - Ensure battery is fully charged
   - Do NOT interrupt flashing process

4. After flashing:
   - Load one of the K38 test .dat files
   - Try to transmit with PTT
   - Check if "DISABLE" message is gone

5. Test with spectrum analyzer and dummy load!

6. If radio is bricked:
   - Reflash with original firmware backup
   - Consult radio manufacturer/forums for recovery

BACKUP FILES:
- Original firmware backup created in patched_firmware/
- Keep this file safe for rollback!
""")

if __name__ == "__main__":
    main()
