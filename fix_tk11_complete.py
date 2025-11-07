#!/usr/bin/env python3
"""
Complete TK11 Channel Fix
==========================
Fixes BOTH mode and frequency issues:
1. Changes USB mode (0x02) → AM mode (0x01)
2. Fixes frequency: multiplies by 10 to get correct CB frequency
   Example: 2.7385 MHz → 27.385 MHz (CB channel)

Usage:
    python3 fix_tk11_complete.py TK11_am.dat TK11_FIXED.dat
"""

import sys
import struct

def fix_channels(input_file, output_file):
    """Fix mode and frequency for all channels"""

    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    print('=' * 90)
    print('TK11 Complete Channel Fix')
    print('=' * 90)
    print(f'Input:  {input_file}')
    print(f'Output: {output_file}')
    print(f'Size:   {len(data):,} bytes')
    print()

    fixed_count = 0

    print('Ch    Original Freq  Fixed Freq    Mode Change    Name')
    print('-' * 90)

    # Process each 64-byte record
    for i in range(len(data) // 64):
        offset = i * 64
        record = data[offset:offset + 64]

        # Get frequency
        freq_hz = struct.unpack('<I', record[0:4])[0]

        # Skip empty channels
        if freq_hz == 0xFFFFFFFF or freq_hz == 0:
            continue

        # Get mode
        mode_byte = record[16]

        # Get name
        name = record[24:32].decode('ascii', errors='ignore').rstrip('\x00')

        # Check if needs fixing
        needs_freq_fix = 2_000_000 <= freq_hz < 10_000_000  # 2-10 MHz range (probably wrong)
        needs_mode_fix = mode_byte == 0x02  # USB mode

        if needs_freq_fix or needs_mode_fix:
            orig_freq_mhz = freq_hz / 1_000_000

            # Fix frequency (multiply by 10)
            if needs_freq_fix:
                new_freq_hz = freq_hz * 10
                data[offset:offset+4] = struct.pack('<I', new_freq_hz)
            else:
                new_freq_hz = freq_hz

            # Fix mode (USB → AM)
            if needs_mode_fix:
                data[offset + 16] = 0x01  # AM mode
                mode_change = 'USB → AM'
            else:
                mode_change = 'OK'

            new_freq_mhz = new_freq_hz / 1_000_000

            print(f'{i:<5} {orig_freq_mhz:>10.4f} MHz  {new_freq_mhz:>10.4f} MHz  {mode_change:<13} {name}')
            fixed_count += 1

    print('-' * 90)
    print(f'Fixed {fixed_count} channels')
    print()

    # Write output
    with open(output_file, 'wb') as f:
        f.write(data)

    print(f'✅ Saved: {output_file}')
    print()
    print('Next steps:')
    print('  1. Open TK11.exe')
    print('  2. Load ' + output_file)
    print('  3. Verify frequencies show correctly (27.xxx MHz, not 2.7xxx MHz)')
    print('  4. Verify modes show as AM')
    print('  5. Upload to radio')
    print('  6. Test TX on correct CB frequencies!')
    print()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 fix_tk11_complete.py <input.dat> <output.dat>')
        print('Example: python3 fix_tk11_complete.py TK11_am.dat TK11_FIXED.dat')
        sys.exit(1)

    fix_channels(sys.argv[1], sys.argv[2])
