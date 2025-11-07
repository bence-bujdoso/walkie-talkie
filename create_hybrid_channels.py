#!/usr/bin/env python3
"""
Create hybrid channel configuration:
- Original channels kept as USB (for receive attempts)
- Duplicate channels created as AM (for transmit)

Usage: python3 create_hybrid_channels.py TK11_am.dat TK11_hybrid.dat
"""

import sys
import struct

def create_hybrid_config(input_file, output_file):
    """Create hybrid USB (RX) + AM (TX) channel config"""

    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    print(f"File size: {len(data)} bytes")
    print(f"Records: {len(data) // 64}")
    print()

    # Find USB channels and their next empty slots
    usb_channels = []
    empty_slot = None

    for i in range(len(data) // 64):
        offset = i * 64
        record = data[offset:offset + 64]

        freq = struct.unpack('<I', record[0:4])[0]
        mode_byte = record[16]
        name = record[24:32].decode('ascii', errors='ignore').rstrip('\x00')

        if freq != 0xFFFFFFFF and mode_byte == 0x02:  # USB channel
            usb_channels.append((i, offset, freq, name))
            print(f"Found USB Ch {i:3d}: {freq/1000000:8.4f} MHz - \"{name}\"")
        elif freq == 0xFFFFFFFF and empty_slot is None:
            empty_slot = i

    print()
    print(f"Found {len(usb_channels)} USB channels")
    print(f"First empty slot: {empty_slot}")
    print()

    # Create AM copies
    if empty_slot is None:
        print("ERROR: No empty slots found for AM copies!")
        return

    for idx, (ch_num, ch_offset, freq, name) in enumerate(usb_channels):
        if empty_slot + idx >= len(data) // 64:
            print(f"WARNING: Not enough space for all AM copies")
            break

        # Copy the USB channel record
        new_offset = (empty_slot + idx) * 64
        data[new_offset:new_offset + 64] = data[ch_offset:ch_offset + 64]

        # Modify to AM mode
        data[new_offset + 16] = 0x01  # AM mode

        # Append " TX" to name if space permits
        new_name = (name + " TX")[:8]
        data[new_offset + 24:new_offset + 32] = new_name.ljust(8, '\x00').encode('ascii')

        print(f"Created AM copy at Ch {empty_slot + idx:3d}: {freq/1000000:8.4f} MHz - \"{new_name}\"")

    # Write output
    with open(output_file, 'wb') as f:
        f.write(data)

    print()
    print(f"Saved: {output_file}")
    print()
    print("Channel layout:")
    print("  - Original USB channels (Ch 0-4): Use for RECEIVE")
    print(f"  - New AM channels (Ch {empty_slot}+): Use for TRANSMIT")
    print()
    print("Next steps:")
    print("  1. Open TK11.exe and load the new file")
    print("  2. Upload to radio")
    print("  3. Use USB channels to listen")
    print("  4. Switch to corresponding AM channel to transmit")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 create_hybrid_channels.py <input.dat> <output.dat>")
        print("Example: python3 create_hybrid_channels.py TK11_am.dat TK11_hybrid.dat")
        sys.exit(1)

    create_hybrid_config(sys.argv[1], sys.argv[2])
