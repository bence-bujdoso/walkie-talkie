#!/usr/bin/env python3
"""
11-Meter Band DSB Unlock Script
Creates CB radio channels (26.965-27.405 MHz) with DSB mode and TX enabled

SAFETY WARNING: This script enables transmission on CB frequencies.
Ensure you have proper authorization and comply with local regulations.
"""

import struct
import shutil
from pathlib import Path
from datetime import datetime

RECORD_SIZE = 64

# CB Channel definitions (40 channels)
CB_CHANNELS = {
    1: (26965000, "CB-1"),
    2: (26975000, "CB-2"),
    3: (26985000, "CB-3"),
    4: (27005000, "CB-4"),
    5: (27015000, "CB-5"),
    6: (27025000, "CB-6"),
    7: (27035000, "CB-7"),
    8: (27055000, "CB-8"),
    9: (27065000, "CB-9"),
    10: (27075000, "CB-10"),
    11: (27085000, "CB-11"),
    12: (27105000, "CB-12"),
    13: (27115000, "CB-13"),
    14: (27125000, "CB-14"),
    15: (27135000, "CB-15"),
    16: (27155000, "CB-16"),
    17: (27165000, "CB-17"),
    18: (27175000, "CB-18"),
    19: (27185000, "CB-19"),  # Popular calling channel
    20: (27205000, "CB-20"),
    21: (27215000, "CB-21"),
    22: (27225000, "CB-22"),
    23: (27255000, "CB-23"),
    24: (27235000, "CB-24"),
    25: (27245000, "CB-25"),
    26: (27265000, "CB-26"),
    27: (27275000, "CB-27"),
    28: (27285000, "CB-28"),
    29: (27295000, "CB-29"),
    30: (27305000, "CB-30"),
    31: (27315000, "CB-31"),
    32: (27325000, "CB-32"),
    33: (27335000, "CB-33"),
    34: (27345000, "CB-34"),
    35: (27355000, "CB-35"),
    36: (27365000, "CB-36"),
    37: (27375000, "CB-37"),
    38: (27385000, "CB-38"),
    39: (27395000, "CB-39"),
    40: (27405000, "CB-40"),
}

def create_channel_record(freq_hz, name, mode_byte_23, tx_enabled=True):
    """
    Create a 64-byte channel record

    Critical bytes:
    - Byte 0-3: RX Frequency (little-endian, Hz)
    - Byte 4-7: TX Frequency (0x00000000 = simplex)
    - Byte 16: Power level (0x02 = standard)
    - Byte 17: Bandwidth (0x00 = standard)
    - Byte 18: Modulation subtype (0x00)
    - Byte 22: TX Permit (0xFF = enabled, 0x00 = disabled)
    - Byte 23: Channel Mode (0x02=FM, 0x04=USB, 0x05=DSB?, 0x06=LSB?)
    - Byte 24-39: Channel name (16 bytes, ASCII, null-padded)
    """
    record = bytearray(RECORD_SIZE)

    # RX Frequency (bytes 0-3)
    record[0:4] = struct.pack('<I', freq_hz)

    # TX Frequency (bytes 4-7) - Simplex
    record[4:8] = struct.pack('<I', 0)

    # CTCSS/DCS (bytes 8-11) - None
    record[8:12] = b'\x00\x00\x00\x00'

    # Unknown flags (bytes 12-15)
    record[12:16] = b'\x00\x00\x00\x00'

    # Power level (byte 16)
    record[16] = 0x02  # Standard power

    # Bandwidth (byte 17)
    record[17] = 0x00  # Standard bandwidth

    # Modulation subtype (byte 18)
    record[18] = 0x00  # Default

    # Scrambler (byte 19)
    record[19] = 0x00  # Off

    # Unknown (bytes 20-21)
    record[20] = 0x00
    record[21] = 0x03  # Observed in K38 USB

    # TX Permit (byte 22) - CRITICAL
    record[22] = 0xFF if tx_enabled else 0x00

    # Channel Mode (byte 23) - CRITICAL FOR DSB
    record[23] = mode_byte_23

    # Channel name (bytes 24-39) - 16 bytes
    name_bytes = name.encode('ascii')[:16]
    record[24:24+len(name_bytes)] = name_bytes
    # Null-pad the rest
    for i in range(24+len(name_bytes), 40):
        record[i] = 0x00

    # Additional settings (bytes 40-47)
    record[40:48] = b'\x00' * 8

    # Reserved (bytes 48-63)
    record[48:64] = b'\x00' * 16

    return bytes(record)

def find_empty_slots(data, count=40):
    """Find empty channel slots to place CB channels"""
    num_records = len(data) // RECORD_SIZE
    empty_slots = []

    for i in range(num_records):
        offset = i * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        # Check if slot is empty (all 0xFF)
        if record[0:4] == b'\xff\xff\xff\xff':
            empty_slots.append(i)
            if len(empty_slots) >= count:
                break

    return empty_slots

def create_11m_dsb_unlock(input_path, output_path, mode_value=0x05, start_channel=1, end_channel=40):
    """
    Create modified TK11.dat with CB channels programmed in DSB mode

    Args:
        input_path: Original TK11.dat
        output_path: Output file
        mode_value: Byte 23 value for DSB mode (0x05, 0x06, or 0x08 to test)
        start_channel: First CB channel to program (1-40)
        end_channel: Last CB channel to program (1-40)
    """

    print("="*80)
    print("11-METER BAND DSB UNLOCK")
    print("="*80)

    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"\nInput file: {input_path}")
    print(f"File size: {len(data):,} bytes")
    print(f"Total channels: {len(data) // RECORD_SIZE}")

    # Find empty slots
    print(f"\nSearching for empty channel slots...")
    empty_slots = find_empty_slots(data, end_channel - start_channel + 1)

    if len(empty_slots) < (end_channel - start_channel + 1):
        print(f"ERROR: Not enough empty slots! Need {end_channel - start_channel + 1}, found {len(empty_slots)}")
        return False

    print(f"Found {len(empty_slots)} empty slots")

    # Create CB channels
    print(f"\nCreating CB channels {start_channel}-{end_channel} with mode byte = 0x{mode_value:02X}")
    print(f"TX: ENABLED on all channels")
    print("-"*80)

    modifications = []

    for idx, cb_num in enumerate(range(start_channel, end_channel + 1)):
        freq_hz, name = CB_CHANNELS[cb_num]
        slot = empty_slots[idx]
        offset = slot * RECORD_SIZE

        # Create channel record
        record = create_channel_record(freq_hz, name, mode_value, tx_enabled=True)

        # Write to data
        data[offset:offset+RECORD_SIZE] = record

        modifications.append({
            'cb_num': cb_num,
            'slot': slot,
            'offset': offset,
            'freq_mhz': freq_hz / 1e6,
            'name': name,
            'mode_byte': mode_value,
        })

        print(f"  CB-{cb_num:2d} @ {freq_hz/1e6:.3f} MHz -> Record {slot:4d} (0x{offset:08X}) - '{name}'")

    # Write output file
    with open(output_path, 'wb') as f:
        f.write(data)

    print("\n" + "="*80)
    print(f"Modified file written to: {output_path}")
    print(f"Total CB channels added: {len(modifications)}")
    print("="*80)

    return modifications

def create_multiple_test_versions(input_path):
    """Create multiple test versions with different mode byte values"""

    print("\n" + "="*80)
    print("CREATING MULTIPLE TEST VERSIONS")
    print("="*80)

    test_modes = [
        (0x05, "DSB Mode (hypothesis 1)"),
        (0x06, "DSB Mode (hypothesis 2)"),
        (0x08, "DSB Mode (hypothesis 3 - bit flag)"),
        (0x01, "AM Mode (for comparison)"),
        (0x03, "LSB Mode (for comparison)"),
    ]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for mode_val, description in test_modes:
        output_name = f"TK11_11M_DSB_MODE_{mode_val:02X}_{timestamp}.dat"
        output_path = Path(input_path).parent / output_name

        print(f"\nCreating test version: Mode 0x{mode_val:02X} - {description}")
        print(f"Output: {output_name}")

        # Only program CB channel 19 (popular calling channel) for testing
        create_11m_dsb_unlock(input_path, output_path, mode_value=mode_val, start_channel=19, end_channel=19)

    print("\n" + "="*80)
    print("TEST VERSIONS COMPLETE")
    print("="*80)
    print("\nTESTING PROCEDURE:")
    print("1. Upload each test file to the radio")
    print("2. Navigate to CB-19 channel")
    print("3. Monitor output on spectrum analyzer or second radio")
    print("4. Press PTT and observe modulation type")
    print("5. Identify which mode byte produces DSB modulation")

def create_full_cb_band(input_path):
    """Create version with all 40 CB channels in DSB mode"""

    print("\n" + "="*80)
    print("CREATING FULL CB BAND (40 CHANNELS)")
    print("="*80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"TK11_CB_FULL_DSB_{timestamp}.dat"
    output_path = Path(input_path).parent / output_name

    # Using 0x05 as best guess for DSB
    # User can modify this after testing
    mode_value = 0x05

    print(f"\nUsing mode byte 0x{mode_value:02X} for DSB")
    print(f"(Adjust this value based on test results)")

    # Backup original
    backup_path = Path(input_path).parent / f"TK11_BACKUP_{timestamp}.dat"
    shutil.copy2(input_path, backup_path)
    print(f"\nBackup created: {backup_path}")

    # Create full CB band
    mods = create_11m_dsb_unlock(input_path, output_path, mode_value=mode_value, start_channel=1, end_channel=40)

    if mods:
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)

        # Verify the file
        with open(output_path, 'rb') as f:
            data = f.read()

        print("\nVerifying first CB channel (CB-1)...")
        record_num = mods[0]['slot']
        offset = record_num * RECORD_SIZE
        record = data[offset:offset+RECORD_SIZE]

        freq = struct.unpack('<I', record[0:4])[0]
        mode = record[23]
        tx_permit = record[22]
        name = record[24:40].decode('ascii', errors='ignore').rstrip('\x00')

        print(f"  Frequency: {freq/1e6:.4f} MHz")
        print(f"  Name: '{name}'")
        print(f"  Mode byte (23): 0x{mode:02X}")
        print(f"  TX Permit (22): 0x{tx_permit:02X} - {'ENABLED' if tx_permit == 0xFF else 'DISABLED'}")

        if freq == 26965000 and mode == mode_value and tx_permit == 0xFF:
            print("\n*** VERIFICATION PASSED ***")
        else:
            print("\n*** VERIFICATION FAILED ***")

def main():
    print("="*80)
    print("11-METER BAND DSB UNLOCK UTILITY")
    print("="*80)
    print("\nThis utility creates CB radio channels with DSB mode enabled.")
    print("\nWARNING: Ensure legal compliance before transmitting!")
    print("="*80)

    input_path = Path(r"E:\AI\tk11\TK11.dat")

    if not input_path.exists():
        print(f"\nERROR: Input file not found: {input_path}")
        return

    # Mode selection
    print("\nOperation modes:")
    print("1. Create test versions (single channel, multiple mode values)")
    print("2. Create full CB band (40 channels, one mode value)")
    print("3. Both")

    choice = input("\nSelect mode (1/2/3) [default: 1]: ").strip() or "1"

    if choice in ["1", "3"]:
        create_multiple_test_versions(input_path)

    if choice in ["2", "3"]:
        create_full_cb_band(input_path)

    print("\n" + "="*80)
    print("OPERATION COMPLETE")
    print("="*80)
    print("\nIMPORTANT SAFETY REMINDERS:")
    print("1. Test with dummy load first")
    print("2. Verify mode with spectrum analyzer")
    print("3. Comply with power limits (4W AM, 12W PEP SSB)")
    print("4. Use only with proper license/authorization")
    print("5. Keep backup of original TK11.dat")
    print("="*80)

if __name__ == "__main__":
    main()
