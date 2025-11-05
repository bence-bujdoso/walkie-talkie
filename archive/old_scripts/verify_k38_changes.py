#!/usr/bin/env python3
"""Quick verification of K38 channel changes"""

import struct
from pathlib import Path

RECORD_SIZE = 64

def read_k38(filepath):
    """Read K38 channel (Record 0) from file"""
    with open(filepath, 'rb') as f:
        data = f.read()

    record = data[0:RECORD_SIZE]

    freq_hz = struct.unpack('<I', record[0:4])[0]
    mode = record[23]
    tx_permit = record[22]
    name = record[24:40].decode('ascii', errors='ignore').rstrip('\x00')

    return {
        'freq_mhz': freq_hz / 1e6,
        'mode': mode,
        'tx_permit': tx_permit,
        'name': name
    }

base_path = Path(r"E:\AI\tk11")

print("="*80)
print("K38 CHANNEL VERIFICATION")
print("="*80)

# Check original
orig_file = base_path / "TK11.dat"
orig = read_k38(orig_file)

print(f"\nORIGINAL TK11.dat:")
print(f"  Name: '{orig['name']}'")
print(f"  Frequency: {orig['freq_mhz']:.4f} MHz")
print(f"  Mode (byte 23): 0x{orig['mode']:02X}")
print(f"  TX Permit: 0x{orig['tx_permit']:02X}")

# Check modified versions
test_modes = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]

print("\n" + "="*80)
print("MODIFIED TEST FILES")
print("="*80)

mode_names = {
    0x00: "FM",
    0x01: "AM",
    0x02: "USB",
    0x03: "LSB",
    0x04: "USB (original)",
    0x05: "DSB? (priority)",
    0x06: "DSB?",
    0x07: "DSB?",
    0x08: "DSB? (bit flag)",
}

# Find the latest timestamp
import glob
pattern = str(base_path / "TK11_K38_MODE_05_*.dat")
files = glob.glob(pattern)
if files:
    latest = max(files)
    # Extract timestamp from filename: TK11_K38_MODE_05_20251029_150652.dat
    parts = latest.split('_')
    timestamp = f"{parts[-2]}_{parts[-1].replace('.dat', '')}"

    print(f"\nTimestamp: {timestamp}")
    print("-"*80)

    for mode_val in test_modes:
        filename = f"TK11_K38_MODE_{mode_val:02X}_{timestamp}.dat"
        filepath = base_path / filename

        if filepath.exists():
            k38 = read_k38(filepath)

            status = "[OK]" if k38['mode'] == mode_val else "[FAIL]"

            print(f"\nMode 0x{mode_val:02X} ({mode_names.get(mode_val, 'Unknown'):15s}) {status}")
            print(f"  File: {filename}")
            print(f"  Name: '{k38['name']}'")
            print(f"  Mode byte: 0x{k38['mode']:02X} (expected 0x{mode_val:02X})")
            print(f"  Frequency: {k38['freq_mhz']:.4f} MHz")
        else:
            print(f"\n[MISSING] {filename}")

print("\n" + "="*80)
print("TESTING INSTRUCTIONS")
print("="*80)
print("""
1. Load TK11_K38_MODE_05_{timestamp}.dat into TK11.exe

2. You should see K38 channel renamed to "K38 DSB 0x05"

3. Upload this file to the radio

4. Select the K38 channel (should show 2.7385 MHz)

5. Connect 50 ohm DUMMY LOAD

6. Use spectrum analyzer to monitor 2.7385 MHz

7. Press PTT and observe:
   - FM: Single carrier with frequency deviation
   - AM: Carrier + 2 symmetrical sidebands (amplitude mod)
   - DSB: Carrier + 2 sidebands (similar to AM but may differ)
   - SSB: Single sideband only

8. If mode 0x05 doesn't produce DSB, try 0x06, 0x07, 0x08

9. Compare with mode 0x00 (FM) and 0x01 (AM) to see difference

PRIORITY TEST: Mode 0x05 (most likely DSB based on analysis)
""")

print("="*80)
