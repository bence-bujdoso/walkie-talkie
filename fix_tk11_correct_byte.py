#!/usr/bin/env python3
"""
CORRECT TK11 Channel Fix - Fixed the right bytes this time!
=============================================================
After deeper analysis, the actual modulation mode is controlled by BYTE 21 (offset 0x15), not byte 16!

Changes:
1. Byte 21 (offset 0x15): Mode selector (0x00=FM, 0x01=AM, 0x02/0x03=USB/LSB)
2. Frequency: Fix 2.7 MHz → 27 MHz for CB channels

Usage:
    python3 fix_tk11_correct_byte.py TK11_am.dat TK11_REALLY_FIXED.dat
"""

import sys
import struct

def fix_channels_correct(input_file, output_file):
    """Fix the CORRECT mode byte (byte 21) and frequency"""

    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    print('=' * 100)
    print('TK11 CORRECT Channel Fix - Using Byte 21 for Mode')
    print('=' * 100)
    print(f'Input:  {input_file}')
    print(f'Output: {output_file}')
    print()

    fixed_count = 0

    print('Ch    Name             Freq Before  Freq After   Byte21 Before  Byte21 After')
    print('-' * 100)

    for i in range(len(data) // 64):
        offset = i * 64
        record = data[offset:offset + 64]

        # Get frequency
        freq_hz = struct.unpack('<I', record[0:4])[0]

        # Skip empty channels
        if freq_hz == 0xFFFFFFFF or freq_hz == 0:
            continue

        # Get ACTUAL mode (byte 21, offset 0x15)
        byte_21_mode = record[21]  # offset 0x15

        # Get name
        name = record[24:32].decode('ascii', errors='ignore').rstrip('\x00')

        # Check if needs fixing
        needs_freq_fix = 2_000_000 <= freq_hz < 10_000_000  # 2-10 MHz
        needs_mode_fix = byte_21_mode in [0x02, 0x03]  # USB/LSB modes

        if needs_freq_fix or needs_mode_fix:
            orig_freq_mhz = freq_hz / 1_000_000

            # Fix frequency
            if needs_freq_fix:
                new_freq_hz = freq_hz * 10
                data[offset:offset+4] = struct.pack('<I', new_freq_hz)
            else:
                new_freq_hz = freq_hz

            # Fix mode (byte 21: USB/LSB → AM)
            if needs_mode_fix:
                old_mode = byte_21_mode
                data[offset + 21] = 0x01  # AM mode
                mode_change = f'0x{old_mode:02X} → 0x01 (AM)'
            else:
                mode_change = 'OK'

            new_freq_mhz = new_freq_hz / 1_000_000

            print(f'{i:<5} {name:<16} {orig_freq_mhz:>9.4f} MHz {new_freq_mhz:>9.4f} MHz  {mode_change}')
            fixed_count += 1

    print('-' * 100)
    print(f'Fixed {fixed_count} channels')
    print()

    # Write output
    with open(output_file, 'wb') as f:
        f.write(data)

    print(f'✅ Saved: {output_file}')
    print()
    print('What was fixed:')
    print('  1. Byte 21 (offset 0x15) changed from USB/LSB (0x02/0x03) → AM (0x01)')
    print('  2. Frequencies multiplied by 10 for CB band (2.7 MHz → 27 MHz)')
    print()
    print('Next steps:')
    print('  1. Load in TK11.exe')
    print('  2. Upload to radio')
    print('  3. Test TX - should work now!')
    print()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 fix_tk11_correct_byte.py <input.dat> <output.dat>')
        print('Example: python3 fix_tk11_correct_byte.py TK11_am.dat TK11_REALLY_FIXED.dat')
        sys.exit(1)

    fix_channels_correct(sys.argv[1], sys.argv[2])
