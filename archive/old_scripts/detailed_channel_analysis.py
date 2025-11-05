#!/usr/bin/env python3
"""
Detailed TK11.dat Channel Record Analysis
Focus on TX lock mechanisms and field structure
"""

import struct
from pathlib import Path

RECORD_SIZE = 64  # Confirmed from pattern analysis

def parse_channel_record(data, record_num):
    """Parse a single 64-byte channel record"""
    offset = record_num * RECORD_SIZE

    if offset + RECORD_SIZE > len(data):
        return None

    record = data[offset:offset+RECORD_SIZE]

    # Parse fields based on observed patterns
    channel_info = {
        'record_num': record_num,
        'offset': offset,

        # Frequency (appears to be 32-bit little-endian at offset 0)
        'rx_frequency_raw': struct.unpack('<I', record[0:4])[0],
        'rx_frequency_mhz': struct.unpack('<I', record[0:4])[0] / 1000000.0,

        # TX offset or separate TX frequency (at offset 4)
        'tx_frequency_raw': struct.unpack('<I', record[4:8])[0],
        'tx_frequency_mhz': struct.unpack('<I', record[4:8])[0] / 1000000.0,

        # CTCSS/DCS codes (offset 8-11)
        'rx_ctcss_raw': struct.unpack('<H', record[8:10])[0],
        'tx_ctcss_raw': struct.unpack('<H', record[10:12])[0],

        # Flags area (offset 12-23)
        'flags_byte_12': record[12],
        'flags_byte_13': record[13],
        'flags_byte_14': record[14],
        'flags_byte_15': record[15],

        # Power/bandwidth/mode flags (offset 16-19)
        'power_flags': record[16],
        'bandwidth_mode': record[17],
        'modulation_mode': record[18],
        'scrambler': record[19],

        # TX permission flags (offset 20-23)
        'tx_permit_byte_20': record[20],
        'tx_permit_byte_21': record[21],
        'tx_permit_byte_22': record[22],  # Often 0xFF in active channels
        'tx_permit_byte_23': record[23],

        # Channel name (offset 24-39, 16 bytes)
        'channel_name_raw': record[24:40],
        'channel_name': record[24:40].decode('ascii', errors='ignore').rstrip('\x00'),

        # Additional settings (offset 40-63)
        'scan_list': record[40],
        'squelch': record[41],
        'tot_timer': record[42],
        'tot_rekey': record[43],

        # More flags
        'optional_signal': record[44],
        'dtmf_id': record[45],
        'ptt_id': record[46],
        'busy_lock': record[47],

        # Unknown/reserved (48-63)
        'reserved_48_63': record[48:64].hex(),

        # Raw record for examination
        'raw_hex': record.hex(),
    }

    return channel_info

def analyze_tx_flags(data):
    """Focus analysis on TX permission flags"""
    print("="*80)
    print("TX PERMISSION FLAG ANALYSIS")
    print("="*80)

    num_records = len(data) // RECORD_SIZE

    # Collect statistics on flag bytes
    flag_stats = {}
    for byte_pos in range(RECORD_SIZE):
        flag_stats[byte_pos] = {}

    active_channels = []
    empty_channels = []

    for i in range(min(num_records, 1000)):  # First 1000 channels
        info = parse_channel_record(data, i)
        if not info:
            break

        # Check if channel is active (has valid frequency)
        if info['rx_frequency_mhz'] > 50 and info['rx_frequency_mhz'] < 2000:
            active_channels.append(info)
        elif info['raw_hex'] == 'ff' * RECORD_SIZE:
            empty_channels.append(info)

    print(f"\nFound {len(active_channels)} active channels")
    print(f"Found {len(empty_channels)} empty (0xFF) channels")

    # Display first 20 active channels
    print("\n" + "="*80)
    print("ACTIVE CHANNEL DETAILS (First 20)")
    print("="*80)

    for idx, info in enumerate(active_channels[:20]):
        print(f"\n--- Channel {info['record_num']} (Offset: {info['offset']:#010x}) ---")
        print(f"Name: '{info['channel_name']}'")
        print(f"RX Frequency: {info['rx_frequency_mhz']:.4f} MHz ({info['rx_frequency_raw']} Hz)")

        if info['tx_frequency_raw'] == 0:
            print(f"TX Frequency: Same as RX (simplex)")
        else:
            print(f"TX Frequency: {info['tx_frequency_mhz']:.4f} MHz ({info['tx_frequency_raw']} Hz)")

        print(f"\nRX CTCSS/DCS: {info['rx_ctcss_raw']:#06x}")
        print(f"TX CTCSS/DCS: {info['tx_ctcss_raw']:#06x}")

        print(f"\nFlag Bytes Analysis:")
        print(f"  Byte 12: {info['flags_byte_12']:#04x}")
        print(f"  Byte 13: {info['flags_byte_13']:#04x}")
        print(f"  Byte 14: {info['flags_byte_14']:#04x}")
        print(f"  Byte 15: {info['flags_byte_15']:#04x}")

        print(f"\nMode/Power Settings:")
        print(f"  Power flags: {info['power_flags']:#04x}")
        print(f"  Bandwidth/Mode: {info['bandwidth_mode']:#04x}")
        print(f"  Modulation: {info['modulation_mode']:#04x}")
        print(f"  Scrambler: {info['scrambler']:#04x}")

        print(f"\n>>> TX PERMIT FLAGS (CRITICAL) <<<")
        print(f"  Byte 20: {info['tx_permit_byte_20']:#04x}")
        print(f"  Byte 21: {info['tx_permit_byte_21']:#04x}")
        print(f"  Byte 22: {info['tx_permit_byte_22']:#04x}  <- Often 0xFF = TX ENABLED")
        print(f"  Byte 23: {info['tx_permit_byte_23']:#04x}")

        print(f"\nAdditional Settings:")
        print(f"  Scan List: {info['scan_list']:#04x}")
        print(f"  Squelch: {info['squelch']:#04x}")
        print(f"  TOT Timer: {info['tot_timer']:#04x}")
        print(f"  Busy Lock: {info['busy_lock']:#04x}")

    # Compare TX flag patterns
    print("\n" + "="*80)
    print("TX FLAG PATTERN COMPARISON")
    print("="*80)

    print("\nByte 22 values in active channels:")
    byte_22_values = {}
    for info in active_channels:
        val = info['tx_permit_byte_22']
        if val not in byte_22_values:
            byte_22_values[val] = []
        byte_22_values[val].append(info['channel_name'])

    for val, channels in sorted(byte_22_values.items()):
        print(f"\n  Value {val:#04x} ({val}): {len(channels)} channels")
        print(f"    Examples: {', '.join(channels[:5])}")

    # Look at other potential TX control bytes
    print("\n" + "="*80)
    print("OTHER POTENTIAL TX CONTROL BYTES")
    print("="*80)

    for byte_pos in [13, 14, 15, 20, 21, 23, 46, 47]:
        print(f"\nByte {byte_pos} value distribution:")
        values = {}
        for info in active_channels:
            record = data[info['offset']:info['offset']+RECORD_SIZE]
            val = record[byte_pos]
            values[val] = values.get(val, 0) + 1

        for val, count in sorted(values.items()):
            print(f"  {val:#04x}: {count} channels")

def create_tx_unlock_patch(data, output_path):
    """Create a patched version with TX unlocked on all channels"""
    print("\n" + "="*80)
    print("CREATING TX-UNLOCKED VERSION")
    print("="*80)

    modified_data = bytearray(data)
    num_records = len(data) // RECORD_SIZE
    modifications = 0

    for i in range(num_records):
        offset = i * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        # Skip empty channels
        if record[0:4] == b'\xff\xff\xff\xff':
            continue

        # Check if channel has valid frequency
        freq = struct.unpack('<I', record[0:4])[0]
        if freq > 50000000 and freq < 2000000000:  # 50 MHz to 2 GHz
            # Hypothesis: Byte 22 = 0xFF enables TX
            # Set it to 0xFF if not already
            if modified_data[offset + 22] != 0xFF:
                print(f"  Channel {i} (offset {offset:#010x}): Byte 22 changed from {modified_data[offset+22]:#04x} to 0xFF")
                modified_data[offset + 22] = 0xFF
                modifications += 1

    print(f"\nTotal modifications: {modifications} channels")

    if modifications > 0:
        with open(output_path, 'wb') as f:
            f.write(modified_data)
        print(f"\nPatched file saved to: {output_path}")
        print("CAUTION: Test this file carefully before using on actual hardware!")
    else:
        print("\nNo modifications needed - all active channels already have TX enabled")

def main():
    file_path = Path(r"E:\AI\tk11\TK11.dat")

    print("="*80)
    print("DETAILED CHANNEL RECORD ANALYSIS - TX LOCK FOCUS")
    print("="*80)
    print(f"File: {file_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    print(f"Record size: {RECORD_SIZE} bytes")
    print(f"Total records: {file_path.stat().st_size // RECORD_SIZE}")

    with open(file_path, 'rb') as f:
        data = f.read()

    # Detailed TX flag analysis
    analyze_tx_flags(data)

    # Offer to create unlocked version
    print("\n" + "="*80)
    output_path = Path(r"E:\AI\tk11\TK11_TX_UNLOCKED.dat")
    create_tx_unlock_patch(data, output_path)

if __name__ == "__main__":
    main()
