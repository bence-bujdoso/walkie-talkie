# Quick Hex Edit Reference for 11-Meter DSB Unlock

## CB Channel Record Template (64 bytes)

### Complete Hex Template

```
Offset | Hex Values | Description
-------|------------|-------------
+0x00  | XX XX XX XX | RX Frequency (Hz, little-endian)
+0x04  | 00 00 00 00 | TX Frequency (simplex)
+0x08  | 00 00       | RX CTCSS/DCS (none)
+0x0A  | 00 00       | TX CTCSS/DCS (none)
+0x0C  | 00 00 00 00 | Unknown flags
+0x10  | 02          | Power level
+0x11  | 00          | Bandwidth
+0x12  | 00          | Modulation subtype
+0x13  | 00          | Scrambler
+0x14  | 00          | Byte 20
+0x15  | 03          | Byte 21
+0x16  | FF          | TX PERMIT (0xFF = ENABLED)
+0x17  | 05          | MODE (0x05 = DSB hypothesis)
+0x18  | XX XX...    | Channel name (16 bytes, ASCII)
+0x28  | 00 00...    | Additional settings (8 bytes)
+0x30  | 00 00...    | Reserved (16 bytes)
```

## CB Channel Frequency Table

| CB | MHz | Hex Bytes (Little-Endian) | Decimal Hz |
|----|-----|---------------------------|------------|
| 1  | 26.965 | `C8 6A 9B 01` | 26,965,000 |
| 2  | 26.975 | `18 7B 9B 01` | 26,975,000 |
| 3  | 26.985 | `68 8B 9B 01` | 26,985,000 |
| 4  | 27.005 | `08 AC 9B 01` | 27,005,000 |
| 5  | 27.015 | `58 BC 9B 01` | 27,015,000 |
| 6  | 27.025 | `A8 CC 9B 01` | 27,025,000 |
| 7  | 27.035 | `F8 DC 9B 01` | 27,035,000 |
| 8  | 27.055 | `98 FD 9B 01` | 27,055,000 |
| 9  | 27.065 | `E8 0D 9C 01` | 27,065,000 |
| 10 | 27.075 | `38 1E 9C 01` | 27,075,000 |
| 11 | 27.085 | `88 2E 9C 01` | 27,085,000 |
| 12 | 27.105 | `28 4F 9C 01` | 27,105,000 |
| 13 | 27.115 | `78 5F 9C 01` | 27,115,000 |
| 14 | 27.125 | `C8 6F 9C 01` | 27,125,000 |
| 15 | 27.135 | `18 80 9C 01` | 27,135,000 |
| 16 | 27.155 | `B8 A0 9C 01` | 27,155,000 |
| 17 | 27.165 | `08 B1 9C 01` | 27,165,000 |
| 18 | 27.175 | `58 C1 9C 01` | 27,175,000 |
| 19 | 27.185 | `48 37 9F 01` | 27,185,000 |
| 20 | 27.205 | `F8 E2 9C 01` | 27,205,000 |
| 21 | 27.215 | `48 F3 9C 01` | 27,215,000 |
| 22 | 27.225 | `98 03 9D 01` | 27,225,000 |
| 23 | 27.255 | `D8 44 9D 01` | 27,255,000 |
| 24 | 27.235 | `E8 13 9D 01` | 27,235,000 |
| 25 | 27.245 | `38 24 9D 01` | 27,245,000 |
| 26 | 27.265 | `28 55 9D 01` | 27,265,000 |
| 27 | 27.275 | `78 65 9D 01` | 27,275,000 |
| 28 | 27.285 | `C8 75 9D 01` | 27,285,000 |
| 29 | 27.295 | `18 86 9D 01` | 27,295,000 |
| 30 | 27.305 | `68 96 9D 01` | 27,305,000 |
| 31 | 27.315 | `B8 A6 9D 01` | 27,315,000 |
| 32 | 27.325 | `08 B7 9D 01` | 27,325,000 |
| 33 | 27.335 | `58 C7 9D 01` | 27,335,000 |
| 34 | 27.345 | `A8 D7 9D 01` | 27,345,000 |
| 35 | 27.355 | `F8 E7 9D 01` | 27,355,000 |
| 36 | 27.365 | `48 F8 9D 01` | 27,365,000 |
| 37 | 27.375 | `98 08 9E 01` | 27,375,000 |
| 38 | 27.385 | `E8 18 9E 01` | 27,385,000 |
| 39 | 27.395 | `38 29 9E 01` | 27,395,000 |
| 40 | 27.405 | `88 CD A1 01` | 27,405,000 |

## Complete Record Examples

### CB Channel 19 (27.185 MHz) - DSB Mode

```
48 37 9F 01 00 00 00 00 00 00 00 00 00 00 00 00
02 00 00 00 00 03 FF 05 43 42 2D 31 39 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

**Breakdown:**
- `48 37 9F 01` = 27,185,000 Hz
- `00 00 00 00` = Simplex (TX = RX)
- `FF` at +0x16 = TX enabled
- `05` at +0x17 = DSB mode (hypothesis)
- `43 42 2D 31 39` = "CB-19"

### CB Channel 1 (26.965 MHz) - DSB Mode

```
C8 6A 9B 01 00 00 00 00 00 00 00 00 00 00 00 00
02 00 00 00 00 03 FF 05 43 42 2D 31 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

### CB Channel 40 (27.405 MHz) - DSB Mode

```
88 CD A1 01 00 00 00 00 00 00 00 00 00 00 00 00
02 00 00 00 00 03 FF 05 43 42 2D 34 30 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

## Manual Hex Edit Procedure

### Step-by-Step: Add CB Channel 19

1. **Open TK11.dat in hex editor**

2. **Find empty slot**
   - Search for: `FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF`
   - Find 64 consecutive FF bytes
   - Note the offset (e.g., `0x00100000`)

3. **Select 64 bytes** starting at that offset

4. **Paste this hex:**
```
48 37 9F 01 00 00 00 00 00 00 00 00 00 00 00 00
02 00 00 00 00 03 FF 05 43 42 2D 31 39 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

5. **Verify critical bytes:**
   - Offset +0x00: `48 37 9F 01` (frequency)
   - Offset +0x16: `FF` (TX enabled)
   - Offset +0x17: `05` (DSB mode)
   - Offset +0x18: `43 42 2D 31 39` ("CB-19")

6. **Save file** as `TK11_CB19_TEST.dat`

7. **Verify file size:** Must be exactly **880,640 bytes**

## Mode Byte Values to Test

| Byte 23 | Expected Mode | Test Priority |
|---------|---------------|---------------|
| `05` | DSB (hypothesis 1) | HIGH |
| `06` | DSB (hypothesis 2) | HIGH |
| `08` | DSB (bit-flag) | MEDIUM |
| `01` | AM (comparison) | LOW |
| `03` | LSB (comparison) | LOW |

## ASCII Character Reference (for names)

| Char | Hex | | Char | Hex | | Char | Hex |
|------|-----|-|------|-----|-|------|-----|
| Space| 20  | | 0 | 30 | | @ | 40 |
| - | 2D | | 1 | 31 | | A | 41 |
| . | 2E | | 2 | 32 | | B | 42 |
| / | 2F | | 3 | 33 | | C | 43 |
|   |    | | 4 | 34 | | D | 44 |
|   |    | | 5 | 35 | | ... | ... |

Example: "CB-19" = `43 42 2D 31 39`

## Frequency Calculation (Python)

```python
import struct

# MHz to hex bytes
def freq_to_hex(mhz):
    hz = int(mhz * 1_000_000)
    return struct.pack('<I', hz).hex().upper()

# Hex bytes to MHz
def hex_to_freq(hex_str):
    bytes_le = bytes.fromhex(hex_str)
    hz = struct.unpack('<I', bytes_le)[0]
    return hz / 1_000_000

# Examples:
print(freq_to_hex(27.185))  # '48379F01'
print(hex_to_freq('48379F01'))  # 27.185
```

## Verification Checklist

After hex editing:

- [ ] File size = 880,640 bytes
- [ ] Frequency bytes are little-endian
- [ ] Byte 22 (offset +0x16) = `FF`
- [ ] Byte 23 (offset +0x17) = mode value
- [ ] Channel name is ASCII, null-padded
- [ ] All other unused bytes = `00`
- [ ] File saved with .dat extension

## Common Mistakes

❌ **Big-endian frequency** (wrong byte order)
- Wrong: `01 9F 37 48`
- Right: `48 37 9F 01`

❌ **TX disabled** (Byte 22 = 00)
- Won't transmit even if mode is correct

❌ **Wrong mode byte position**
- Mode is at +0x17 (Byte 23), not +0x12 (Byte 18)

❌ **Name not null-padded**
- Must fill remaining bytes with `00`, not `FF`

❌ **File size changed**
- Must remain exactly 880,640 bytes

## Tool Recommendations

**Free Hex Editors:**
- **HxD** (Windows) - Recommended
- **010 Editor** (Cross-platform, has templates)
- **ImHex** (Cross-platform, modern)
- **Hex Fiend** (Mac)

**Features Needed:**
- Search/replace
- Block select
- Goto offset
- File comparison
- Checksum calculation

---

**END OF REFERENCE**
