#!/usr/bin/env python3
"""
Use dnSpy Console to decompile TK11.exe
"""

import subprocess
import os
import sys
from pathlib import Path

def decompile_with_dnspy():
    """Decompile TK11.exe using dnSpy Console"""

    # Check if files exist
    dnspy = Path("dnSpy/dnSpy.Console.exe")
    tk11_exe = Path("TK11.exe")

    if not dnspy.exists():
        print(f"ERROR: {dnspy} not found!")
        return False

    if not tk11_exe.exists():
        print(f"ERROR: {tk11_exe} not found!")
        return False

    # Create output directory
    output_dir = Path("tk11_decompiled")
    output_dir.mkdir(exist_ok=True)

    print(f"[*] Decompiling TK11.exe using dnSpy Console...")
    print(f"[*] Output directory: {output_dir}")

    # Run dnSpy Console
    # Usage: dnSpy.Console.exe <assembly> --output <dir>
    try:
        cmd = [str(dnspy), str(tk11_exe), "-o", str(output_dir)]

        print(f"[*] Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        print("\n--- STDOUT ---")
        print(result.stdout)

        if result.stderr:
            print("\n--- STDERR ---")
            print(result.stderr)

        if result.returncode == 0:
            print(f"\n[+] Decompilation successful!")
            print(f"[+] Check {output_dir} for .cs files")

            # List generated files
            cs_files = list(output_dir.rglob("*.cs"))
            print(f"\n[+] Found {len(cs_files)} C# files:")
            for f in cs_files[:10]:
                print(f"    - {f}")
            if len(cs_files) > 10:
                print(f"    ... and {len(cs_files) - 10} more")

            return True
        else:
            print(f"\n[-] Decompilation failed with return code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("ERROR: Decompilation timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def search_for_validation_code(decompiled_dir):
    """Search through decompiled code for validation functions"""

    print("\n[*] Searching for validation code...")

    decompiled_path = Path(decompiled_dir)
    if not decompiled_path.exists():
        print(f"ERROR: {decompiled_path} not found!")
        return

    cs_files = list(decompiled_path.rglob("*.cs"))

    validation_files = []

    for cs_file in cs_files:
        try:
            with open(cs_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Search for validation-related keywords
                if any(keyword in content for keyword in [
                    "File version is Wrong",
                    "文件版本错误",
                    "ValidateFirmware",
                    "CheckFirmware",
                    "FirmwareValidation"
                ]):
                    validation_files.append(cs_file)
                    print(f"[+] Found in: {cs_file.name}")

        except Exception as e:
            print(f"[-] Error reading {cs_file}: {e}")

    if validation_files:
        print(f"\n[+] Found {len(validation_files)} files with validation code!")
        print("\n[*] Extracting relevant code sections...")

        for vf in validation_files:
            print(f"\n{'='*80}")
            print(f"FILE: {vf}")
            print('='*80)

            try:
                with open(vf, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                    # Find lines around the error message
                    for i, line in enumerate(lines):
                        if "File version is Wrong" in line or "文件版本错误" in line:
                            # Print context (50 lines before and after)
                            start = max(0, i - 50)
                            end = min(len(lines), i + 50)

                            print(f"\n--- Context around line {i+1} ---\n")
                            for j in range(start, end):
                                marker = ">>>" if j == i else "   "
                                print(f"{marker} {j+1:4d}: {lines[j]}", end='')

                # Save to a separate file
                output_file = Path("validation_code_extracted.cs")
                with open(vf, 'r', encoding='utf-8') as src:
                    with open(output_file, 'w', encoding='utf-8') as dst:
                        dst.write(f"// Extracted from: {vf}\n")
                        dst.write(src.read())

                print(f"\n[+] Full code saved to: {output_file}")

            except Exception as e:
                print(f"[-] Error: {e}")

    else:
        print("[-] No validation code found in decompiled files")
        print("[*] Trying alternative search...")

        # Search for any file with "version" or "valid" in the name
        for cs_file in cs_files:
            if any(keyword in cs_file.name.lower() for keyword in ['version', 'valid', 'firmware', 'update']):
                print(f"[*] Potentially relevant file: {cs_file.name}")

def main():
    print("="*80)
    print("TK11.exe Decompilation with dnSpy Console")
    print("="*80 + "\n")

    # Step 1: Decompile
    if decompile_with_dnspy():
        # Step 2: Search for validation code
        search_for_validation_code("tk11_decompiled")
    else:
        print("\n[-] Decompilation failed!")
        print("\n[*] Alternative: Use dnSpy GUI manually")
        print("    1. Run: dnSpy/dnSpy.exe")
        print("    2. Open: TK11.exe")
        print("    3. Search: 'File version is Wrong' (Ctrl+Shift+K)")

if __name__ == "__main__":
    main()