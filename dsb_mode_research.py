#!/usr/bin/env python3
"""
DSB Mode Research
Search firmware for DSB (Double Sideband) mode references and capabilities
"""

import struct
from pathlib import Path

def search_mode_strings(data):
    """Search for modulation mode strings"""
    print("="*80)
    print("SEARCHING FOR MODULATION MODE STRINGS")
    print("="*80)

    mode_keywords = [
        (b'DSB', 'DSB (Double Sideband)'),
        (b'dsb', 'dsb (lowercase)'),
        (b'USB', 'USB (Upper Sideband)'),
        (b'LSB', 'LSB (Lower Sideband)'),
        (b'SSB', 'SSB (Single Sideband)'),
        (b'AM', 'AM (Amplitude Modulation)'),
        (b'FM', 'FM (Frequency Modulation)'),
        (b'CW', 'CW (Continuous Wave)'),
        (b'NFM', 'NFM (Narrow FM)'),
        (b'WFM', 'WFM (Wide FM)'),
    ]

    results = {}

    for keyword, desc in mode_keywords:
        positions = []
        offset = 0
        while True:
            pos = data.find(keyword, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1

        if positions:
            results[desc] = positions
            print(f"\n[FOUND] {desc}: {len(positions)} occurrence(s)")
            for pos in positions[:5]:
                # Context
                start = max(0, pos - 32)
                end = min(len(data), pos + 32)
                context = data[start:end]
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
                print(f"  @ 0x{pos:08X}: {ascii_str}")
        else:
            print(f"\n[NOT FOUND] {desc}")

    return results

def search_cb_references(data):
    """Search for CB radio references"""
    print("\n" + "="*80)
    print("SEARCHING FOR CB RADIO REFERENCES")
    print("="*80)

    cb_keywords = [
        b'CB',
        b'27MHz',
        b'27 MHz',
        b'11m',
        b'11M',
        b'11 meter',
        b'citizen',
        b'CITIZEN',
    ]

    for keyword in cb_keywords:
        positions = []
        offset = 0
        while True:
            pos = data.find(keyword, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1

        if positions:
            print(f"\n[FOUND] '{keyword.decode('ascii', errors='ignore')}': {len(positions)} occurrence(s)")
            for pos in positions[:3]:
                start = max(0, pos - 32)
                end = min(len(data), pos + 32)
                context = data[start:end]
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
                print(f"  @ 0x{pos:08X}: {ascii_str}")

def analyze_k38_usb_channel(data_path):
    """Analyze the K38 USB channel to understand USB mode encoding"""
    print("\n" + "="*80)
    print("ANALYZING 'K38 USB' CHANNEL STRUCTURE")
    print("="*80)

    with open(data_path, 'rb') as f:
        data = f.read()

    RECORD_SIZE = 64

    # From frequency scanner, K38 USB is at 2.7385 MHz
    # Let's find it
    target_freq = 2738500  # Hz

    num_records = len(data) // RECORD_SIZE

    for i in range(num_records):
        offset = i * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        if record[0:4] == b'\xff\xff\xff\xff':
            continue

        freq = struct.unpack('<I', record[0:4])[0]

        if freq == target_freq:
            print(f"\nFound K38 USB at Record {i}, Offset 0x{offset:08X}")
            print(f"\nFull record hex dump:")

            for j in range(0, RECORD_SIZE, 16):
                chunk = record[j:j+16]
                hex_str = ' '.join(f'{b:02X}' for b in chunk)
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                print(f"  +{j:02X}: {hex_str:<48}  {ascii_str}")

            print(f"\nKey bytes:")
            print(f"  Byte 18 (Modulation): 0x{record[18]:02X} ({record[18]})")
            print(f"  Byte 22 (TX Permit):  0x{record[22]:02X} ({record[22]})")
            print(f"  Byte 23 (Chan Type):  0x{record[23]:02X} ({record[23]})")

            print(f"\nChannel name: '{record[24:40].decode('ascii', errors='ignore').rstrip(chr(0))}'")

            # Compare with K14 FM
            print("\n" + "-"*80)
            print("COMPARISON: Looking for K14 FM channel...")

            k14_freq = 2712500  # Hz
            for k in range(num_records):
                k_offset = k * RECORD_SIZE
                k_record = data[k_offset:k_offset+RECORD_SIZE]
                k_freq = struct.unpack('<I', k_record[0:4])[0]

                if k_freq == k14_freq:
                    print(f"\nFound K14 FM at Record {k}, Offset 0x{k_offset:08X}")
                    print(f"  Byte 18 (Modulation): 0x{k_record[18]:02X} ({k_record[18]})")
                    print(f"  Byte 22 (TX Permit):  0x{k_record[22]:02X} ({k_record[22]})")
                    print(f"  Byte 23 (Chan Type):  0x{k_record[23]:02X} ({k_record[23]})")

                    print("\n*** COMPARISON ***")
                    print(f"K38 USB - Byte 18: 0x{record[18]:02X}, Byte 23: 0x{record[23]:02X}")
                    print(f"K14 FM  - Byte 18: 0x{k_record[18]:02X}, Byte 23: 0x{k_record[23]:02X}")

                    if record[23] == 0x04 and k_record[23] == 0x02:
                        print("\n*** KEY FINDING ***")
                        print("Byte 23 appears to be the PRIMARY mode selector:")
                        print("  0x02 = FM mode")
                        print("  0x04 = USB/SSB mode")
                    break

            break

def create_dsb_hypothesis():
    """Create hypothesis about DSB mode"""
    print("\n" + "="*80)
    print("DSB MODE HYPOTHESIS")
    print("="*80)

    print("""
Based on radio firmware analysis patterns:

BYTE 23 (Channel Type/Mode) appears to be the PRIMARY modulation selector:
  0x02 = FM (Frequency Modulation)
  0x04 = USB (Upper Side Band) / SSB mode

HYPOTHESIZED VALUES for DSB:
  0x05 = DSB (Double Side Band) - Most likely
  0x06 = DSB variant
  0x08 = DSB (if bit-flag based)

BYTE 18 (Modulation) currently shows 0x00 for all channels in TK11.dat,
suggesting it may be:
  - Unused in this firmware version
  - OR used for sub-modes within each channel type
  - OR bandwidth settings

TESTING STRATEGY:
  1. Create a test channel on 11m band (e.g., 27.185 MHz - CB Channel 19)
  2. Set Byte 23 to different values (0x05, 0x06, 0x08) to test DSB
  3. Ensure Byte 22 (TX Permit) = 0xFF to enable transmission
  4. Test each configuration to see which produces DSB modulation

ALTERNATIVE APPROACH:
  If firmware doesn't support DSB natively:
  - DSB = AM with carrier (not suppressed)
  - May need to set AM mode (if available) with specific carrier settings
  - Byte 17 or other bytes might control carrier suppression

CB LEGAL CONSIDERATIONS:
  - CB channels 1-40 (26.965-27.405 MHz) in USA
  - Legal modes: AM (carrier), SSB (USB/LSB)
  - DSB is essentially AM with both sidebands
  - Power limits: 4W AM, 12W PEP SSB
""")

def main():
    print("="*80)
    print("DSB MODE RESEARCH")
    print("="*80)

    firmware_path = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    dat_path = Path(r"E:\AI\tk11\TK11.dat")

    if firmware_path.exists():
        print(f"\nAnalyzing firmware: {firmware_path}")
        with open(firmware_path, 'rb') as f:
            fw_data = f.read()

        search_mode_strings(fw_data)
        search_cb_references(fw_data)
    else:
        print(f"\nFirmware not found: {firmware_path}")

    if dat_path.exists():
        analyze_k38_usb_channel(dat_path)

    create_dsb_hypothesis()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
