#!/usr/bin/env python3
"""
TK11 Direct Memory Patcher - CORRECTED VERSION
Patches TX mask in CPS .dat file to enable USB TX mode

IMPORTANT: Uses 0x17 (not 0x13) for proper USB TX functionality!
"""

import sys
import os
import shutil

def patch_cps_file(dat_file_path, create_backup=True):
    """
    Patch the TX mask in a CPS .dat file

    Args:
        dat_file_path: Path to the .dat file
        create_backup: Whether to create a backup before modifying
    """

    TX_MASK_OFFSET = 0x314D
    ORIGINAL_VALUE = 0x03
    NEW_VALUE = 0x17  # ⭐ CORRECTED: 0x17 enables USB TX!

    if not os.path.exists(dat_file_path):
        print(f"❌ ERROR: File not found: {dat_file_path}")
        return False

    # Create backup if requested
    if create_backup:
        backup_path = dat_file_path + '.backup'
        shutil.copy2(dat_file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")

    # Read the file
    with open(dat_file_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\n📁 Loaded file: {dat_file_path}")
    print(f"   Size: {len(data):,} bytes ({len(data)/1024:.1f} KB)")

    # Check offset validity
    if TX_MASK_OFFSET >= len(data):
        print(f"❌ ERROR: Offset 0x{TX_MASK_OFFSET:04X} is beyond file size!")
        return False

    # Show current value
    current = data[TX_MASK_OFFSET]
    print(f"\n🔍 Current TX mask at offset 0x{TX_MASK_OFFSET:04X}:")
    print(f"   Hex: 0x{current:02X}")
    print(f"   Binary: {bin(current)} ({current:08b})")
    print(f"   Decimal: {current}")

    # Validate current value
    if current != ORIGINAL_VALUE:
        print(f"\n⚠️  WARNING: Expected 0x{ORIGINAL_VALUE:02X} but found 0x{current:02X}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return False

    # Apply patch
    data[TX_MASK_OFFSET] = NEW_VALUE

    print(f"\n✅ New TX mask: 0x{NEW_VALUE:02X}")
    print(f"   Binary: {bin(NEW_VALUE)} ({NEW_VALUE:08b})")
    print(f"   Decimal: {NEW_VALUE}")
    print(f"\n🎯 TX Modes Enabled:")
    print(f"   - Bit 0 (0x01): FM  ✓")
    print(f"   - Bit 1 (0x02): AM  ✓")
    print(f"   - Bit 2 (0x04): USB ✓ ⭐ NOW ENABLED!")
    print(f"   - Bit 4 (0x10): WFM ✓")

    # Save modified file
    output_file = dat_file_path.replace('.dat', '_PATCHED.dat')
    if output_file == dat_file_path:  # If no .dat extension
        output_file = dat_file_path + '_PATCHED'

    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"\n💾 Patched file saved: {output_file}")

    print(f"\n📋 Next Steps:")
    print(f"   1. Open TK11.exe (original version - no patches needed!)")
    print(f"   2. Click 'Write' or 'Upload to radio'")
    print(f"   3. Select: {output_file}")
    print(f"   4. Wait for write completion")
    print(f"   5. Radio will restart")
    print(f"   6. Navigate to K38 channel (27.385 MHz)")
    print(f"   7. Connect 50Ω dummy load (CRITICAL!)")
    print(f"   8. Select USB mode")
    print(f"   9. Press PTT - should work without 'DISABLE' message!")
    print(f"   10. SUCCESS! 🎉")

    return True

def verify_patch(dat_file_path):
    """Verify if a .dat file has been patched"""
    TX_MASK_OFFSET = 0x314D
    NEW_VALUE = 0x17

    if not os.path.exists(dat_file_path):
        print(f"❌ File not found: {dat_file_path}")
        return False

    with open(dat_file_path, 'rb') as f:
        f.seek(TX_MASK_OFFSET)
        value = f.read(1)[0]

    if value == NEW_VALUE:
        print(f"✅ File is PATCHED: TX mask = 0x{value:02X} (USB TX enabled)")
        return True
    else:
        print(f"❌ File is NOT patched: TX mask = 0x{value:02X}")
        return False

def main():
    print("="*70)
    print("TK11 Direct Memory Patcher - CORRECTED VERSION")
    print("="*70)
    print("Patches TX mask to 0x17 to enable USB TX mode")
    print("="*70)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print(f"  Patch:  python {sys.argv[0]} <TK11_BACKUP.dat>")
        print(f"  Verify: python {sys.argv[0]} --verify <TK11_BACKUP.dat>")
        print("\nExample:")
        print(f"  python {sys.argv[0]} TK11_BACKUP.dat")
        sys.exit(1)

    if sys.argv[1] == '--verify':
        if len(sys.argv) < 3:
            print("Error: Specify file to verify")
            sys.exit(1)
        success = verify_patch(sys.argv[2])
        sys.exit(0 if success else 1)

    dat_file = sys.argv[1]
    success = patch_cps_file(dat_file)

    if success:
        print("\n✅ SUCCESS! Ready to write to radio!")
    else:
        print("\n❌ FAILED! Check errors above.")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
