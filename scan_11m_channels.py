#!/usr/bin/env python3
"""
11-Meter Band Channel Scanner
Identifies CB radio frequencies (26.965-27.405 MHz) in TK11.dat
and analyzes their modulation mode settings
"""

import struct
from pathlib import Path

RECORD_SIZE = 64
CB_FREQ_MIN = 26965000  # 26.965 MHz in Hz
CB_FREQ_MAX = 27405000  # 27.405 MHz in Hz

# Standard CB channels for reference
CB_CHANNELS = {
    1: 26965000,
    2: 26975000,
    3: 26985000,
    4: 27005000,
    5: 27015000,
    6: 27025000,
    7: 27035000,
    8: 27055000,
    9: 27065000,
    10: 27075000,
    11: 27085000,
    12: 27105000,
    13: 27115000,
    14: 27125000,
    15: 27135000,
    16: 27155000,
    17: 27165000,
    18: 27175000,
    19: 27185000,
    20: 27205000,
    21: 27215000,
    22: 27225000,
    23: 27255000,
    24: 27235000,
    25: 27245000,
    26: 27265000,
    27: 27275000,
    28: 27285000,
    29: 27295000,
    30: 27305000,
    31: 27315000,
    32: 27325000,
    33: 27335000,
    34: 27345000,
    35: 27355000,
    36: 27365000,
    37: 27375000,
    38: 27385000,
    39: 27395000,
    40: 27405000,
}

def parse_channel(data, record_num):
    """Parse a single 64-byte channel record"""
    offset = record_num * RECORD_SIZE
    if offset + RECORD_SIZE > len(data):
        return None

    record = data[offset:offset+RECORD_SIZE]

    # Check if empty channel
    if record[0:4] == b'\xff\xff\xff\xff':
        return None

    return {
        'record_num': record_num,
        'offset': offset,
        'rx_freq_hz': struct.unpack('<I', record[0:4])[0],
        'tx_freq_hz': struct.unpack('<I', record[4:8])[0],
        'rx_ctcss': struct.unpack('<H', record[8:10])[0],
        'tx_ctcss': struct.unpack('<H', record[10:12])[0],
        'byte_12': record[12],
        'byte_13': record[13],
        'byte_14': record[14],
        'byte_15': record[15],
        'power_level': record[16],
        'bandwidth': record[17],
        'modulation': record[18],  # Byte 18 - MODULATION MODE
        'scrambler': record[19],
        'byte_20': record[20],
        'byte_21': record[21],
        'tx_permit': record[22],  # Byte 22 - TX PERMIT
        'channel_type': record[23],  # Byte 23 - CHANNEL TYPE/MODE
        'name': record[24:40].decode('ascii', errors='ignore').rstrip('\x00'),
        'scan_list': record[40],
        'squelch': record[41],
        'tot': record[42],
        'raw': record,
    }

def find_11m_channels(data):
    """Find all channels in the 11-meter CB band"""
    num_records = len(data) // RECORD_SIZE
    cb_channels = []

    print("="*80)
    print("SCANNING FOR 11-METER BAND CHANNELS (26.965 - 27.405 MHz)")
    print("="*80)

    for i in range(num_records):
        channel = parse_channel(data, i)
        if not channel:
            continue

        freq = channel['rx_freq_hz']
        if CB_FREQ_MIN <= freq <= CB_FREQ_MAX:
            cb_channels.append(channel)

    print(f"\nFound {len(cb_channels)} channels in 11-meter band")
    return cb_channels

def analyze_modulation_modes(cb_channels):
    """Analyze modulation mode bytes"""
    print("\n" + "="*80)
    print("MODULATION MODE ANALYSIS")
    print("="*80)

    # Collect statistics
    mod_values = {}
    byte_23_values = {}

    for ch in cb_channels:
        mod = ch['modulation']
        mod_values[mod] = mod_values.get(mod, 0) + 1

        b23 = ch['channel_type']
        byte_23_values[b23] = byte_23_values.get(b23, 0) + 1

    print("\nByte 18 (Modulation) values found:")
    for val, count in sorted(mod_values.items()):
        print(f"  0x{val:02X} ({val}): {count} channels")

    print("\nByte 23 (Channel Type) values found:")
    for val, count in sorted(byte_23_values.items()):
        print(f"  0x{val:02X} ({val}): {count} channels")

    return mod_values, byte_23_values

def display_channel_details(cb_channels):
    """Display detailed information for each 11m channel"""
    print("\n" + "="*80)
    print("DETAILED 11-METER CHANNEL INFORMATION")
    print("="*80)

    for ch in cb_channels:
        freq_mhz = ch['rx_freq_hz'] / 1000000.0
        print(f"\n--- Record {ch['record_num']} @ offset 0x{ch['offset']:08X} ---")
        print(f"Name: '{ch['name']}'")
        print(f"RX Frequency: {freq_mhz:.4f} MHz ({ch['rx_freq_hz']} Hz)")

        if ch['tx_freq_hz'] == 0:
            print(f"TX Frequency: Simplex (same as RX)")
        else:
            tx_mhz = ch['tx_freq_hz'] / 1000000.0
            print(f"TX Frequency: {tx_mhz:.4f} MHz ({ch['tx_freq_hz']} Hz)")

        # Check if it matches a standard CB channel
        matching_cb = None
        for cb_num, cb_freq in CB_CHANNELS.items():
            if abs(ch['rx_freq_hz'] - cb_freq) < 1000:  # Within 1 kHz
                matching_cb = cb_num
                break

        if matching_cb:
            print(f"*** MATCHES CB Channel {matching_cb} ***")

        print(f"\nCritical Bytes:")
        print(f"  Byte 18 (Modulation):  0x{ch['modulation']:02X} ({ch['modulation']})")
        print(f"  Byte 22 (TX Permit):   0x{ch['tx_permit']:02X} ({ch['tx_permit']})  {'[ENABLED]' if ch['tx_permit'] == 0xFF else '[DISABLED]'}")
        print(f"  Byte 23 (Chan Type):   0x{ch['channel_type']:02X} ({ch['channel_type']})")

        print(f"\nOther Settings:")
        print(f"  Byte 16 (Power):       0x{ch['power_level']:02X}")
        print(f"  Byte 17 (Bandwidth):   0x{ch['bandwidth']:02X}")
        print(f"  Byte 19 (Scrambler):   0x{ch['scrambler']:02X}")

        # Show raw hex of critical region (bytes 16-23)
        critical = ch['raw'][16:24]
        print(f"\nBytes 16-23 (hex): {' '.join(f'{b:02X}' for b in critical)}")

def analyze_all_modulation_values(data):
    """Scan ALL channels to understand modulation byte values"""
    print("\n" + "="*80)
    print("SCANNING ALL CHANNELS FOR MODULATION PATTERNS")
    print("="*80)

    num_records = len(data) // RECORD_SIZE
    modulation_stats = {}

    for i in range(num_records):
        channel = parse_channel(data, i)
        if not channel:
            continue

        mod = channel['modulation']
        if mod not in modulation_stats:
            modulation_stats[mod] = {
                'count': 0,
                'examples': []
            }

        modulation_stats[mod]['count'] += 1
        if len(modulation_stats[mod]['examples']) < 3:
            modulation_stats[mod]['examples'].append({
                'name': channel['name'],
                'freq': channel['rx_freq_hz'] / 1000000.0,
                'byte_23': channel['channel_type']
            })

    print("\nModulation byte (Byte 18) distribution across ALL channels:")
    for mod_val in sorted(modulation_stats.keys()):
        info = modulation_stats[mod_val]
        print(f"\n  0x{mod_val:02X} ({mod_val}): {info['count']} channels")
        print(f"    Examples:")
        for ex in info['examples']:
            print(f"      '{ex['name']}' @ {ex['freq']:.4f} MHz, Byte23=0x{ex['byte_23']:02X}")

    return modulation_stats

def create_mode_hypothesis():
    """Create hypothesis about modulation mode values"""
    print("\n" + "="*80)
    print("MODULATION MODE HYPOTHESIS")
    print("="*80)

    print("\nBased on typical radio firmware patterns:")
    print("  0x00 = FM (Frequency Modulation)")
    print("  0x01 = AM (Amplitude Modulation)")
    print("  0x02 = NFM (Narrow FM) or USB")
    print("  0x03 = LSB (Lower Side Band)")
    print("  0x04 = USB (Upper Side Band)")
    print("  0x05 = CW (Continuous Wave)")
    print("  0x06 = DSB (Double Side Band) - RARE")
    print("  0x07 = WFM (Wide FM)")
    print("\nNote: Byte 23 may also be involved in mode selection")
    print("From TX_UNLOCK_REPORT.md:")
    print("  Byte 23 observed: 0x02 = FM mode, 0x04 = USB/Other mode")

def main():
    file_path = Path(r"E:\AI\tk11\TK11.dat")

    print("="*80)
    print("11-METER BAND (CB) CHANNEL SCANNER")
    print("="*80)
    print(f"File: {file_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    print(f"Record size: {RECORD_SIZE} bytes")
    print(f"Total capacity: {file_path.stat().st_size // RECORD_SIZE} channels")

    with open(file_path, 'rb') as f:
        data = f.read()

    # 1. Find all 11m channels
    cb_channels = find_11m_channels(data)

    if not cb_channels:
        print("\n*** NO 11-METER BAND CHANNELS FOUND ***")
        print("This radio may not have CB frequencies programmed.")
        return

    # 2. Analyze modulation modes in 11m channels
    mod_stats, byte23_stats = analyze_modulation_modes(cb_channels)

    # 3. Display detailed info
    display_channel_details(cb_channels)

    # 4. Analyze all channels for context
    all_mod_stats = analyze_all_modulation_values(data)

    # 5. Create hypothesis
    create_mode_hypothesis()

    # 6. Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n11-meter band channels found: {len(cb_channels)}")

    if cb_channels:
        tx_enabled = sum(1 for ch in cb_channels if ch['tx_permit'] == 0xFF)
        tx_disabled = len(cb_channels) - tx_enabled
        print(f"  TX Enabled:  {tx_enabled}")
        print(f"  TX Disabled: {tx_disabled}")

        print(f"\nFrequency range: {min(ch['rx_freq_hz'] for ch in cb_channels)/1e6:.4f} - {max(ch['rx_freq_hz'] for ch in cb_channels)/1e6:.4f} MHz")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
