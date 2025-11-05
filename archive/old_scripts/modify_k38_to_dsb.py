#!/usr/bin/env python3
"""
Modify K38 channel to test different DSB mode values
Changes only the modulation byte (byte 23) of the existing K38 channel
"""

import struct
import shutil
from pathlib import Path
from datetime import datetime

RECORD_SIZE = 64

def read_channel_record(data, record_num):
    """Read a channel record and parse it"""
    offset = record_num * RECORD_SIZE
    record = data[offset:offset+RECORD_SIZE]

    freq_hz = struct.unpack('<I', record[0:4])[0]
    tx_freq_hz = struct.unpack('<I', record[4:8])[0]
    tx_permit = record[22]
    mode = record[23]
    name = record[24:40].decode('ascii', errors='ignore').rstrip('\x00')

    return {
        'record_num': record_num,
        'offset': offset,
        'freq_hz': freq_hz,
        'freq_mhz': freq_hz / 1e6,
        'tx_freq_hz': tx_freq_hz,
        'tx_permit': tx_permit,
        'mode': mode,
        'name': name,
        'raw_record': record
    }

def modify_k38_mode(input_path, output_path, new_mode_byte, rename_channel=True):
    """
    Modify K38 channel (Record 0) to use a different mode byte

    Args:
        input_path: Original TK11.dat
        output_path: Output file
        new_mode_byte: New value for byte 23 (mode)
        rename_channel: If True, rename "K38 USB" to "K38 DSB"
    """

    print("="*80)
    print(f"MODIFYING K38 CHANNEL - MODE BYTE TEST")
    print("="*80)

    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nInput file: {input_path}")
    print(f"Output file: {output_path}")

    # Read K38 channel (Record 0)
    k38_before = read_channel_record(data, 0)

    print(f"\n--- K38 CHANNEL (Record 0) - BEFORE ---")
    print(f"Offset: 0x{k38_before['offset']:08X}")
    print(f"Frequency: {k38_before['freq_mhz']:.4f} MHz")
    print(f"Name: '{k38_before['name']}'")
    print(f"Mode (byte 23): 0x{k38_before['mode']:02X}")
    print(f"TX Permit (byte 22): 0x{k38_before['tx_permit']:02X}")

    # Modify byte 23 (mode)
    offset_byte_23 = 0 * RECORD_SIZE + 23
    data[offset_byte_23] = new_mode_byte

    print(f"\n--- MODIFICATION ---")
    print(f"Changing mode byte 23: 0x{k38_before['mode']:02X} -> 0x{new_mode_byte:02X}")

    # Optionally rename channel
    if rename_channel:
        new_name = f"K38 DSB 0x{new_mode_byte:02X}"
        name_offset = 0 * RECORD_SIZE + 24

        # Clear old name
        for i in range(16):
            data[name_offset + i] = 0x00

        # Write new name
        name_bytes = new_name.encode('ascii')[:16]
        data[name_offset:name_offset+len(name_bytes)] = name_bytes

        print(f"Renaming channel: '{k38_before['name']}' -> '{new_name}'")

    # Write output file
    with open(output_path, 'wb') as f:
        f.write(data)

    # Verify
    with open(output_path, 'rb') as f:
        verify_data = f.read()

    k38_after = read_channel_record(verify_data, 0)

    print(f"\n--- K38 CHANNEL (Record 0) - AFTER ---")
    print(f"Frequency: {k38_after['freq_mhz']:.4f} MHz")
    print(f"Name: '{k38_after['name']}'")
    print(f"Mode (byte 23): 0x{k38_after['mode']:02X}")
    print(f"TX Permit (byte 22): 0x{k38_after['tx_permit']:02X}")

    # Verify change
    if k38_after['mode'] == new_mode_byte:
        print(f"\n*** VERIFICATION PASSED ***")
        return True
    else:
        print(f"\n*** VERIFICATION FAILED ***")
        return False

def create_test_versions(input_path):
    """Create multiple test versions with different mode bytes for K38"""

    print("\n" + "="*80)
    print("CREATING K38 DSB TEST VERSIONS")
    print("="*80)

    test_modes = [
        (0x00, "FM Mode (baseline)"),
        (0x01, "AM Mode (baseline)"),
        (0x02, "USB Mode (original)"),
        (0x03, "LSB Mode (test)"),
        (0x04, "USB Mode (original value, no change)"),
        (0x05, "DSB Mode (hypothesis 1) ***PRIORITY***"),
        (0x06, "DSB Mode (hypothesis 2)"),
        (0x07, "DSB Mode (hypothesis 3)"),
        (0x08, "DSB Mode (hypothesis 4 - bit flag)"),
    ]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = Path(input_path).parent

    # Create backup first
    backup_path = base_path / f"TK11_BACKUP_{timestamp}.dat"
    shutil.copy2(input_path, backup_path)
    print(f"\nBackup created: {backup_path.name}")

    print(f"\nCreating test versions...")
    print("-"*80)

    success_count = 0

    for mode_val, description in test_modes:
        output_name = f"TK11_K38_MODE_{mode_val:02X}_{timestamp}.dat"
        output_path = base_path / output_name

        print(f"\n[{mode_val+1}/{len(test_modes)}] Mode 0x{mode_val:02X} - {description}")

        success = modify_k38_mode(input_path, output_path, mode_val, rename_channel=True)

        if success:
            success_count += 1
            print(f"[OK] Created: {output_name}")
        else:
            print(f"[FAILED] {output_name}")

    print("\n" + "="*80)
    print("TEST VERSIONS COMPLETE")
    print("="*80)
    print(f"\nSuccessfully created: {success_count}/{len(test_modes)} files")

    print(f"\nAll files saved to: {base_path}")

    print("\n" + "="*80)
    print("TESTING PROCEDURE")
    print("="*80)
    print("""
1. Load TK11_K38_MODE_05_{timestamp}.dat into TK11.exe (PRIORITY TEST)
   - This should show K38 channel with mode changed

2. Upload to radio

3. Select K38 channel on radio

4. Connect 50Ω DUMMY LOAD to antenna connector

5. Use SPECTRUM ANALYZER or second receiver to monitor 2.7385 MHz

6. Press PTT and observe modulation:
   - FM: Single carrier, frequency deviation
   - AM: Carrier + 2 sidebands (amplitude modulation)
   - DSB: Carrier + 2 sidebands (double sideband)
   - SSB: 1 sideband only (no carrier or suppressed carrier)

7. If mode 0x05 works for DSB, that's the correct value!
   If not, test 0x06, 0x07, 0x08

8. Compare with baseline:
   - Mode 0x00 (FM) - should be standard FM
   - Mode 0x01 (AM) - should be standard AM
   - Mode 0x02 (USB) - may or may not work

IMPORTANT:
- Test on 2.7385 MHz (K38 frequency)
- This frequency is likely LEGAL for testing (not FM broadcast)
- Use dummy load to avoid interference
- Measure with spectrum analyzer to confirm modulation type
""")

def create_cb_k38_version(input_path):
    """Create version where K38 is changed to CB Channel 19 (27.185 MHz) with DSB"""

    print("\n" + "="*80)
    print("CREATING K38 → CB-19 CONVERSION")
    print("="*80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = Path(input_path).parent
    output_name = f"TK11_K38_CB19_DSB_{timestamp}.dat"
    output_path = base_path / output_name

    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nConverting K38 channel to CB-19...")

    # Record 0 modifications
    offset = 0

    # Change frequency to CB-19: 27.185 MHz = 27,185,000 Hz
    cb19_freq = 27_185_000
    data[offset+0:offset+4] = struct.pack('<I', cb19_freq)

    # TX frequency = simplex (0)
    data[offset+4:offset+8] = struct.pack('<I', 0)

    # Mode byte 23 = 0x05 (DSB hypothesis)
    data[offset+23] = 0x05

    # TX permit byte 22 = 0xFF (enabled)
    data[offset+22] = 0xFF

    # Change name to "CB-19 DSB"
    new_name = "CB-19 DSB"
    data[offset+24:offset+40] = b'\x00' * 16  # Clear
    name_bytes = new_name.encode('ascii')
    data[offset+24:offset+24+len(name_bytes)] = name_bytes

    # Write output
    with open(output_path, 'wb') as f:
        f.write(data)

    # Verify
    with open(output_path, 'rb') as f:
        verify_data = f.read()

    k38_after = read_channel_record(verify_data, 0)

    print(f"\n--- CONVERTED CHANNEL (Record 0) ---")
    print(f"Frequency: {k38_after['freq_mhz']:.4f} MHz (was 2.7385 MHz)")
    print(f"Name: '{k38_after['name']}' (was 'K38 USB')")
    print(f"Mode (byte 23): 0x{k38_after['mode']:02X} (DSB)")
    print(f"TX Permit (byte 22): 0x{k38_after['tx_permit']:02X} (enabled)")

    if abs(k38_after['freq_mhz'] - 27.185) < 0.001 and k38_after['mode'] == 0x05:
        print(f"\n*** VERIFICATION PASSED ***")
        print(f"\nFile created: {output_name}")
        print(f"\nThis version converts K38 to CB-19 (27.185 MHz) with DSB mode.")
        print(f"Use this for testing DSB on CB band!")
        return True
    else:
        print(f"\n*** VERIFICATION FAILED ***")
        return False

def main():
    print("="*80)
    print("K38 CHANNEL DSB MODE TEST UTILITY")
    print("="*80)
    print("""
This utility modifies the EXISTING K38 channel to test DSB modes.
TK11.exe will definitely see this channel since it already exists!

We will:
1. Keep the same record position (Record 0)
2. Keep the frequency (2.7385 MHz) OR change to CB-19
3. Change ONLY the mode byte (byte 23)
4. Optionally rename the channel
""")

    input_path = Path(r"E:\AI\tk11\TK11.dat")

    if not input_path.exists():
        print(f"\nERROR: Input file not found: {input_path}")
        return

    print("\n" + "="*80)
    print("SELECT OPERATION MODE")
    print("="*80)
    print("1. Create test versions on original frequency (2.7385 MHz)")
    print("2. Convert K38 to CB-19 (27.185 MHz) with DSB mode")
    print("3. Both")

    choice = input("\nSelect mode (1/2/3) [default: 1]: ").strip() or "1"

    if choice in ["1", "3"]:
        create_test_versions(input_path)

    if choice in ["2", "3"]:
        create_cb_k38_version(input_path)

    print("\n" + "="*80)
    print("OPERATION COMPLETE")
    print("="*80)
    print("\nIMPORTANT:")
    print("- Load the generated files into TK11.exe")
    print("- The K38 channel WILL BE VISIBLE (it already exists)")
    print("- Test with DUMMY LOAD and SPECTRUM ANALYZER")
    print("- Determine which mode byte produces DSB modulation")
    print("="*80)

if __name__ == "__main__":
    main()
