#!/usr/bin/env python3
"""
Analyze TK11.exe to find and potentially patch the validation code
"""

from pathlib import Path
import struct

def find_error_message_location(exe_path):
    """Find the 'File version is Wrong!' error message and nearby code"""

    with open(exe_path, 'rb') as f:
        data = f.read()

    error_msg = b"File version is Wrong"
    offset = data.find(error_msg)

    if offset == -1:
        print("Error message not found!")
        return None

    print("="*80)
    print("FOUND ERROR MESSAGE")
    print("="*80)
    print(f"\nError message at offset: 0x{offset:08X}")

    # Show context around the error message
    context_start = max(0, offset - 100)
    context_end = min(len(data), offset + len(error_msg) + 100)
    context = data[context_start:context_end]

    print("\nContext (hex):")
    for i in range(0, len(context), 16):
        line = context[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in line)
        addr = context_start + i
        print(f"  {addr:08X}: {hex_str}")

    # Search backwards for potential validation code
    # Look for comparison instructions before the error message
    print("\n" + "="*80)
    print("SEARCHING FOR VALIDATION CODE")
    print("="*80)
    print("""
In .NET/C# applications (which TK11.exe appears to be based on 'mscorlib'),
the validation is likely in managed code.

We need to:
1. Decompile the .NET assembly
2. Find the validation function
3. Patch it to always return true

However, there's a simpler approach:
- Find where the error is displayed
- Patch that code path to never execute
- Or find the validation check (likely comparing a checksum/signature)
- NOP out the check or make it always succeed

For .NET apps, we should use dnSpy or similar to decompile and patch.
""")

    return offset

def search_for_signature_validation(exe_path):
    """Search for cryptographic signature validation patterns"""

    with open(exe_path, 'rb') as f:
        data = f.read()

    print("\n" + "="*80)
    print("SEARCHING FOR CRYPTO/VALIDATION PATTERNS")
    print("="*80)

    patterns = [
        (b"signature", "signature validation"),
        (b"Signature", "Signature validation"),
        (b"SIGNATURE", "SIGNATURE validation"),
        (b"crypto", "cryptographic"),
        (b"Crypto", "Cryptographic"),
        (b"verify", "verification"),
        (b"Verify", "Verification"),
        (b"checksum", "checksum"),
        (b"Checksum", "Checksum"),
        (b"hash", "hash"),
        (b"Hash", "Hash"),
        (b"SHA", "SHA hashing"),
        (b"MD5", "MD5 hashing"),
        (b"CRC", "CRC checking"),
    ]

    for pattern, desc in patterns:
        offset = 0
        count = 0
        while True:
            offset = data.find(pattern, offset)
            if offset == -1:
                break
            count += 1
            if count <= 3:  # Only show first 3 occurrences
                print(f"\nFound '{pattern.decode('ascii', errors='ignore')}' at 0x{offset:08X}")
            offset += 1

        if count > 0:
            print(f"  Total occurrences: {count}")

def create_patched_exe_instructions():
    """Provide instructions for patching TK11.exe"""

    print("\n" + "="*80)
    print("RECOMMENDED APPROACH: PATCH TK11.EXE")
    print("="*80)
    print("""
Since the firmware appears to be cryptographically protected,
we should patch TK11.exe to skip the validation instead.

OPTION 1: Use dnSpy (Recommended for .NET apps)
--------------------------------------------
1. Download dnSpy: https://github.com/dnSpy/dnSpy/releases
2. Open TK11.exe in dnSpy
3. Search for "File version is Wrong"
4. Find the validation function
5. Patch it to always return true/skip validation
6. Save patched executable

OPTION 2: Binary patch (if we can identify the exact location)
--------------------------------------------
1. Find the conditional jump that checks validation
2. Change it to an unconditional jump (always skip error)
3. Or NOP out the error display code

OPTION 3: Alternative approach - Direct radio programming
--------------------------------------------
If the radio supports it, we could:
1. Connect to radio via USB/serial
2. Write directly to radio memory (bypass TK11.exe)
3. Modify the TX enable mask in RAM
4. Make it permanent (if supported)

Let me create a backup of TK11.exe first...
""")

def main():
    exe_path = Path(r"E:\AI\tk11\TK11.exe")

    if not exe_path.exists():
        print(f"ERROR: {exe_path} not found!")
        return

    # Create backup
    backup_path = Path(r"E:\AI\tk11\TK11_ORIGINAL_BACKUP.exe")
    if not backup_path.exists():
        import shutil
        shutil.copy2(exe_path, backup_path)
        print(f"[OK] Backup created: {backup_path.name}\n")

    find_error_message_location(exe_path)
    search_for_signature_validation(exe_path)
    create_patched_exe_instructions()

if __name__ == "__main__":
    main()
