#!/usr/bin/env python3
"""
Patch TK11.exe to bypass firmware version check

This allows loading patched firmware files that fail version validation.
"""

import shutil
from pathlib import Path
from datetime import datetime

def find_version_check_code(data):
    """Find version check patterns in TK11.exe"""

    print("="*80)
    print("SEARCHING FOR VERSION CHECK CODE IN TK11.EXE")
    print("="*80)

    patterns_to_find = [
        b'File version',
        b'File Version',
        b'version',
        b'Version',
        b'Wrong',
        b'WRONG',
        b'Error',
        b'ERROR',
        b'.bin',
        b'.BIN',
    ]

    findings = []

    for pattern in patterns_to_find:
        offset = 0
        while True:
            offset = data.find(pattern, offset)
            if offset == -1:
                break

            # Get context
            start = max(0, offset - 32)
            end = min(len(data), offset + 64)
            context = data[start:end]

            findings.append({
                'pattern': pattern,
                'offset': offset,
                'context': context,
                'context_start': start
            })

            offset += 1

    findings.sort(key=lambda x: x['offset'])

    print(f"\nFound {len(findings)} potential version check locations:\n")

    for f in findings:
        try:
            pattern_str = f['pattern'].decode('ascii', errors='ignore')
        except:
            pattern_str = f['pattern'].hex()

        print(f"Offset 0x{f['offset']:08X}: '{pattern_str}'")

        # Show context
        ctx = f['context']
        ctx_start = f['context_start']

        for i in range(0, min(len(ctx), 64), 16):
            line = ctx[i:i+16]
            hex_str = ' '.join(f'{b:02x}' for b in line)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)
            print(f"  {ctx_start + i:08X}: {hex_str:<48} {ascii_str}")
        print()

    return findings

def patch_version_check_simple(data):
    """
    Simple approach: Find "File version is Wrong" string and NOP nearby comparison
    """

    print("\n" + "="*80)
    print("ATTEMPTING SIMPLE PATCH (String-based)")
    print("="*80)

    # Find error message
    error_msg = b'File version is Wrong'
    offset = data.find(error_msg)

    if offset == -1:
        error_msg = b'Wrong'
        offset = data.find(error_msg)

    if offset == -1:
        print("\n[ERROR] Could not find version error message")
        return None

    print(f"\n[OK] Found error message at offset: 0x{offset:08X}")

    # The comparison that triggers this error is usually within 100-500 bytes before the string
    # Look for common x86 comparison opcodes
    search_start = max(0, offset - 500)
    search_end = offset

    search_region = data[search_start:search_end]

    # Look for common comparison patterns:
    # - JE/JZ (74 xx) - Jump if Equal
    # - JNE/JNZ (75 xx) - Jump if Not Equal
    # - CMP (39/3B/3C/3D/80/81/83) - Compare
    # - TEST (84/85) - Test

    print(f"\nSearching for comparison instructions in range 0x{search_start:08X}-0x{search_end:08X}")

    # Find all JNE/JE instructions
    jump_instrs = []

    for i in range(len(search_region) - 1):
        if search_region[i] in [0x74, 0x75]:  # JE/JNE
            actual_offset = search_start + i
            jump_target = search_region[i+1]
            jump_instrs.append({
                'offset': actual_offset,
                'opcode': search_region[i],
                'opcode_name': 'JE' if search_region[i] == 0x74 else 'JNE',
                'target': jump_target
            })

    print(f"\nFound {len(jump_instrs)} conditional jump instructions:")
    for jmp in jump_instrs[-10:]:  # Show last 10 (closest to error message)
        print(f"  0x{jmp['offset']:08X}: {jmp['opcode_name']} {jmp['target']:02X}")

    if not jump_instrs:
        print("\n[WARNING] No conditional jumps found near error message")
        return None

    # The last JNE before the error message is likely the version check
    last_jne = None
    for jmp in reversed(jump_instrs):
        if jmp['opcode'] == 0x75:  # JNE
            last_jne = jmp
            break

    if last_jne:
        print(f"\n[OK] Most likely version check: JNE at 0x{last_jne['offset']:08X}")
        print(f"    Patch: Change JNE (75) to NOP NOP (90 90)")
        return last_jne['offset']
    else:
        # Try last JE
        last_je = jump_instrs[-1] if jump_instrs else None
        if last_je:
            print(f"\n[OK] Alternative: JE at 0x{last_je['offset']:08X}")
            print(f"    Patch: Invert JE (74) to JNE (75) or NOP (90 90)")
            return last_je['offset']

    return None

def apply_patch(data, offset, patch_type='nop'):
    """Apply patch at given offset"""

    if patch_type == 'nop':
        # Replace JNE with NOP NOP
        data[offset] = 0x90
        data[offset + 1] = 0x90
        print(f"\n[OK] Applied NOP patch at 0x{offset:08X}")
    elif patch_type == 'invert':
        # Invert conditional jump
        if data[offset] == 0x74:  # JE -> JNE
            data[offset] = 0x75
        elif data[offset] == 0x75:  # JNE -> JE
            data[offset] = 0x74
        print(f"\n[OK] Applied invert patch at 0x{offset:08X}")

    return data

def create_patched_exe(input_path, output_path):
    """Create patched TK11.exe"""

    print("="*80)
    print("TK11.EXE VERSION CHECK BYPASS PATCHER")
    print("="*80)

    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nInput: {input_path}")
    print(f"Size: {len(data):,} bytes")

    # Find version check
    findings = find_version_check_code(data)

    # Try simple patch
    patch_offset = patch_version_check_simple(data)

    if patch_offset is None:
        print("\n[ERROR] Could not automatically find patch location")
        print("\nManual intervention required:")
        print("  1. Use a disassembler (IDA Pro, Ghidra)")
        print("  2. Find the 'File version is Wrong' string reference")
        print("  3. Trace back to the version check comparison")
        print("  4. Patch the conditional jump")
        return False

    # Apply patch
    data = apply_patch(data, patch_offset, 'nop')

    # Write patched file
    with open(output_path, 'wb') as f:
        f.write(data)

    print(f"\n[OK] Patched EXE written to: {output_path}")

    # Verify
    with open(output_path, 'rb') as f:
        verify_data = f.read()

    if verify_data[patch_offset:patch_offset+2] == b'\x90\x90':
        print(f"\n[OK] Verification passed - patch applied correctly")
        return True
    else:
        print(f"\n[ERROR] Verification failed")
        return False

def main():
    print("="*80)
    print("TK11.EXE VERSION CHECK BYPASS")
    print("="*80)
    print("""
This tool patches TK11.exe to skip firmware version validation.

WHAT IT DOES:
- Finds the version check code in TK11.exe
- Patches the conditional jump to bypass the check
- Allows loading patched firmware files

WARNINGS:
- Modifies TK11.exe (backup will be created)
- May not work if code structure is different
- Use at your own risk

""")

    response = input("Continue? (type 'YES'): ")
    if response != 'YES':
        print("Aborted.")
        return

    base_path = Path(r"E:\AI\tk11")
    input_exe = base_path / "TK11.exe"
    output_dir = base_path / "patched_tk11_exe"

    if not input_exe.exists():
        print(f"\n[ERROR] TK11.exe not found: {input_exe}")
        return

    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Backup
    backup_exe = output_dir / f"TK11_ORIGINAL_{timestamp}.exe"
    shutil.copy2(input_exe, backup_exe)
    print(f"\n[OK] Backup created: {backup_exe.name}")

    # Patch
    output_exe = output_dir / f"TK11_PATCHED_NOVERCHECK_{timestamp}.exe"

    success = create_patched_exe(input_exe, output_exe)

    if success:
        print("\n" + "="*80)
        print("PATCH SUCCESSFUL!")
        print("="*80)
        print(f"""
Patched TK11.exe created: {output_exe.name}

NEXT STEPS:

1. Use patched TK11.exe instead of original:
   - Rename original TK11.exe to TK11_original.exe
   - Copy patched exe as TK11.exe
   OR
   - Launch patched exe directly

2. Try loading patched firmware:
   File -> Flash Firmware -> TK11_PATCHED_USB_TX_ENABLE_*.bin

3. Should no longer show "File version is Wrong" error

4. If still doesn't work:
   - Try different patch approach (manual)
   - Or try to fix firmware checksum instead

BACKUP:
Original TK11.exe saved as: {backup_exe.name}
""")
    else:
        print("\n[ERROR] Patching failed")
        print("\nAlternative approach needed:")
        print("  1. Manual disassembly and patching")
        print("  2. Fix firmware checksum")
        print("  3. Use alternative firmware flash method")

if __name__ == "__main__":
    main()
