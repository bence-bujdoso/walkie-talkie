#!/usr/bin/env python3
"""
Verification Suite for TK11 Patches
Tests both firmware and TK11.exe patches
"""

import os
import struct
from pathlib import Path

class PatchVerifier:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []

    def verify_firmware_patch(self, firmware_path):
        """Verify firmware has USB TX unlock"""
        print(f"\n[*] Verifying firmware: {firmware_path}")

        if not os.path.exists(firmware_path):
            self.errors.append(f"Firmware not found: {firmware_path}")
            return False

        with open(firmware_path, 'rb') as f:
            data = f.read()

        # Check file size
        if len(data) < 0x314D + 1:
            self.errors.append(f"Firmware too small: {len(data)} bytes")
            return False

        # Check TX mask at offset 0x314D
        tx_mask = data[0x314D]

        if tx_mask == 0x13:
            self.success.append(f"✅ USB TX enabled (0x13) at offset 0x314D")
            return True
        elif tx_mask == 0x03:
            self.warnings.append(f"⚠️  USB TX still disabled (0x03) at offset 0x314D")
            return False
        else:
            self.warnings.append(f"⚠️  Unexpected TX mask value: 0x{tx_mask:02X}")
            return False

    def verify_tk11_exe_size(self, exe_path):
        """Check if TK11.exe was modified (size change)"""
        print(f"\n[*] Checking TK11.exe: {exe_path}")

        if not os.path.exists(exe_path):
            self.errors.append(f"TK11.exe not found: {exe_path}")
            return False

        size = os.path.getsize(exe_path)
        original_size = 390656  # Known original size

        if size == original_size:
            self.warnings.append(f"⚠️  TK11.exe size unchanged ({size} bytes)")
            self.warnings.append("    This might be the original, unpatched version")
            return False
        else:
            self.success.append(f"✅ TK11.exe size changed: {size} bytes (was {original_size})")
            self.success.append("    This suggests the file was modified")
            return True

    def verify_backup_exists(self):
        """Check if backup was created"""
        print("\n[*] Checking for backup files...")

        backup_files = [
            "TK11_ORIGINAL_BACKUP.exe",
            "TK11_ORIGINAL_FINAL.exe",
            "TK11_ORIGINAL_FINAL_BACKUP.exe"
        ]

        found_backup = False
        for backup in backup_files:
            if os.path.exists(backup):
                self.success.append(f"✅ Backup found: {backup}")
                found_backup = True

        if not found_backup:
            self.warnings.append("⚠️  No backup found! Create backup before patching:")
            self.warnings.append("    copy TK11.exe TK11_ORIGINAL_BACKUP.exe")

        return found_backup

    def verify_patched_firmware_directory(self):
        """Check if patched firmware files exist"""
        print("\n[*] Checking patched firmware directory...")

        firmware_dir = Path("patched_firmware_final")

        if not firmware_dir.exists():
            self.warnings.append(f"⚠️  Directory not found: {firmware_dir}")
            self.warnings.append("    Run: python create_perfect_firmware.py")
            return False

        # Find all .bin files
        bin_files = list(firmware_dir.glob("*.bin"))

        if not bin_files:
            self.warnings.append(f"⚠️  No .bin files in {firmware_dir}")
            return False

        self.success.append(f"✅ Found {len(bin_files)} firmware files:")
        for f in bin_files:
            self.success.append(f"    - {f.name}")

        # Verify each firmware
        all_valid = True
        for firmware in bin_files:
            if not self.verify_firmware_patch(firmware):
                all_valid = False

        return all_valid

    def print_report(self):
        """Print verification report"""
        print("\n" + "="*80)
        print("VERIFICATION REPORT")
        print("="*80)

        if self.success:
            print("\n✅ SUCCESS:")
            for msg in self.success:
                print(f"  {msg}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for msg in self.warnings:
                print(f"  {msg}")

        if self.errors:
            print("\n❌ ERRORS:")
            for msg in self.errors:
                print(f"  {msg}")

        # Overall status
        print("\n" + "="*80)
        if self.errors:
            print("❌ VERIFICATION FAILED")
            print("Fix errors above before continuing")
            return False
        elif self.warnings:
            print("⚠️  VERIFICATION PASSED WITH WARNINGS")
            print("Review warnings above")
            return True
        else:
            print("✅ VERIFICATION PASSED - ALL GOOD!")
            return True

def main():
    print("="*80)
    print("TK11 PATCH VERIFICATION SUITE")
    print("="*80)

    verifier = PatchVerifier()

    # 1. Check for backup
    verifier.verify_backup_exists()

    # 2. Check patched firmware directory
    verifier.verify_patched_firmware_directory()

    # 3. Check TK11.exe
    tk11_paths = [
        "TK11.exe",
        "TK11_PATCHED_COMPLETE.exe",
        "patched_tk11_exe/TK11_PATCHED_NOVERCHECK_20251029_170355.exe"
    ]

    for tk11 in tk11_paths:
        if os.path.exists(tk11):
            verifier.verify_tk11_exe_size(tk11)

    # Print report
    success = verifier.print_report()

    if success:
        print("\n[+] Ready to test!")
        print("\nNext steps:")
        print("  1. Copy patched TK11.exe")
        print("     copy TK11_PATCHED_COMPLETE.exe TK11.exe")
        print("  2. Launch TK11.exe")
        print("  3. Load firmware: patched_firmware_final\\TK11_PATCHED_v3_minimal.bin")
        print("  4. Flash to radio")
    else:
        print("\n[-] Fix issues before testing")

if __name__ == "__main__":
    main()
