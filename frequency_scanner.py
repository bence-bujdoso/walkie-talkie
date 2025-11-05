#!/usr/bin/env python3
"""
Frequency Scanner - Show what frequencies are actually in TK11.dat
"""

import struct
from pathlib import Path
from collections import defaultdict

RECORD_SIZE = 64

def parse_channel(data, record_num):
    """Parse a single 64-byte channel record"""
    offset = record_num * RECORD_SIZE
    if offset + RECORD_SIZE > len(data):
        return None

    record = data[offset:offset+RECORD_SIZE]

    # Check if empty channel
    if record[0:4] == b'\xff\xff\xff\xff':
        return None

    freq_hz = struct.unpack('<I', record[0:4])[0]

    # Filter out invalid frequencies
    if freq_hz < 1000000 or freq_hz > 3000000000:  # 1 MHz to 3 GHz
        return None

    return {
        'record_num': record_num,
        'offset': offset,
        'rx_freq_hz': freq_hz,
        'tx_freq_hz': struct.unpack('<I', record[4:8])[0],
        'modulation': record[18],
        'tx_permit': record[22],
        'channel_type': record[23],
        'name': record[24:40].decode('ascii', errors='ignore').rstrip('\x00'),
        'raw': record,
    }

def scan_frequencies(data):
    """Scan all frequencies and group by band"""
    num_records = len(data) // RECORD_SIZE

    bands = {
        'HF': (1.8e6, 30e6),          # HF including CB
        'VHF_LOW': (30e6, 88e6),      # VHF Low (incl 6m, 4m, etc)
        'FM_BROADCAST': (88e6, 108e6), # FM Broadcast
        'VHF_HIGH': (108e6, 174e6),   # VHF High (incl 2m ham)
        'UHF': (300e6, 512e6),        # UHF (incl 70cm ham)
        'UHF_HIGH': (512e6, 960e6),   # UHF High
        'OTHER': (0, 3000e6),         # Everything else
    }

    band_channels = defaultdict(list)
    all_channels = []

    for i in range(num_records):
        channel = parse_channel(data, i)
        if not channel:
            continue

        all_channels.append(channel)
        freq = channel['rx_freq_hz']

        classified = False
        for band_name, (fmin, fmax) in bands.items():
            if fmin <= freq < fmax:
                band_channels[band_name].append(channel)
                classified = True
                break

        if not classified:
            band_channels['OTHER'].append(channel)

    print("="*80)
    print("FREQUENCY DISTRIBUTION BY BAND")
    print("="*80)

    for band_name in ['HF', 'VHF_LOW', 'FM_BROADCAST', 'VHF_HIGH', 'UHF', 'UHF_HIGH', 'OTHER']:
        channels = band_channels[band_name]
        if channels:
            freqs = [ch['rx_freq_hz']/1e6 for ch in channels]
            print(f"\n{band_name}:")
            print(f"  Count: {len(channels)}")
            print(f"  Range: {min(freqs):.4f} - {max(freqs):.4f} MHz")
            print(f"  First 5 channels:")
            for ch in channels[:5]:
                print(f"    {ch['rx_freq_hz']/1e6:8.4f} MHz - '{ch['name']}' - Mod:0x{ch['modulation']:02X} TX:0x{ch['tx_permit']:02X}")

    # Check specifically for CB range
    print("\n" + "="*80)
    print("CHECKING CB BAND (26.965 - 27.405 MHz)")
    print("="*80)

    cb_min = 26.965e6
    cb_max = 27.405e6
    cb_channels = [ch for ch in all_channels if cb_min <= ch['rx_freq_hz'] <= cb_max]

    if cb_channels:
        print(f"\n*** FOUND {len(cb_channels)} CB CHANNELS ***")
        for ch in cb_channels:
            print(f"  {ch['rx_freq_hz']/1e6:.4f} MHz - '{ch['name']}'")
    else:
        print("\n*** NO CB CHANNELS FOUND ***")

        # Check for nearby frequencies
        hf_channels = [ch for ch in all_channels if 2e6 <= ch['rx_freq_hz'] <= 30e6]
        if hf_channels:
            print(f"\nHF channels found ({len(hf_channels)} total):")
            for ch in sorted(hf_channels, key=lambda x: x['rx_freq_hz'])[:10]:
                print(f"  {ch['rx_freq_hz']/1e6:.6f} MHz - '{ch['name']}'")
        else:
            print("\nNo HF channels found at all (2-30 MHz)")

    return all_channels

def main():
    file_path = Path(r"E:\AI\tk11\TK11.dat")

    print("="*80)
    print("FREQUENCY SCANNER")
    print("="*80)

    with open(file_path, 'rb') as f:
        data = f.read()

    channels = scan_frequencies(data)

    print("\n" + "="*80)
    print(f"Total valid channels found: {len(channels)}")
    print("="*80)

if __name__ == "__main__":
    main()
