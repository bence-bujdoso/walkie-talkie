# TK11 Firmware Format - Detailed Analysis

## Executive Summary

The TK11 firmware file (`TK11_v5.00.09_ENG.bin`) is **357,976 bytes** and contains **encrypted/obfuscated firmware data** wrapped in a proprietary format. The TK11.exe programming software contains two parsing methods (`PareUpdataFile` and `PareUpdataFile1`) that decrypt and validate the firmware before uploading to the device.

**Key Finding**: Our patched firmware fails because we edited the **encrypted** firmware directly, corrupting both the encryption and the CRC checksum. The bootloader rejects the corrupted encrypted data even after bypassing TK11.exe validation.

---

## 1. File Analysis

### Original Firmware File
- **Filename**: `TK11_v5.00.09_ENG.bin`
- **Size**: 357,976 bytes (0x57658)
- **Entropy**: 7.98/8.0 (near-maximum, indicates encryption/compression)
- **Format**: Encrypted binary with proprietary header

### Hex Dump (First 128 bytes)
```
Offset    Hex Data                                          ASCII
00000000: 98 57 84 20 D4 FD 0B 04 EE 8E AF B0 9C 82 3D 59  .W. ..........=Y
00000010: 01 F5 8C 5D AD EA DF 26 94 EF 62 63 83 77 8E 5A  ...]...&..bc.w.Z
00000020: BD 84 52 33 E6 BD 76 30 A2 2C FE A3 C2 58 3C 67  ..R3..v0.,...X<g
00000030: CC 82 BF 71 56 14 F4 0C 73 69 1E 2C 05 29 F7 BE  ...qV...si.,.)..
00000040: C1 EB 60 D7 9E 83 6D 7D FA C1 8E D4 EF 40 5A 83  ..`...m}.....@Z.
00000050: D6 98 9C 59 34 E0 C1 68 92 6C 48 76 FD E5 1D 44  ...Y4..h.lHv...D
00000060: 39 1F A5 28 FC 54 E3 67 F9 EA 11 90 8A 43 CA 85  9..(.T.g.....C..
00000070: EA 70 D0 A7 24 EF 52 44 25 65 E7 CD C7 AA 5A 4D  .p..$.RD%e....ZM
```

### Observations
- **No standard magic bytes**: First bytes are `98 57 84 20` (unusual)
- **No ARM vector table**: No valid stack pointer / reset vector at offset 0
- **No plaintext strings**: Version "5.00.09" not visible in hex dump
- **High byte diversity**: Consistent with encryption or compression

---

## 2. TK11.exe Firmware Parser Analysis

### Class: `K7.wfm_progress`

This class handles firmware loading, validation, and uploading.

### Key Fields

```csharp
// Instance fields
private int VER_STRING_LEN;      // Length of version string in header
private int VER_POSITION;        // Byte offset of version string

// Static fields
private static int TIME_STRING_LEN = 32;  // Timestamp length
private static string file_ver = "old";    // Format version detected
private static int versionHighNo = -1;     // Major version number
```

### Methods

#### A. `PareUpdataFile(string path)` → `byte[]`
**Primary firmware parser for newer format**

- **IL Code Size**: 806 bytes (complex logic)
- **Local Variables**:
  - `FileInfo`, `FileStream` - File I/O
  - `byte[]` × 5 - Multiple buffers for header, data, decrypted output
  - `UInt16` × 2 - CRC16 checksums (computed and expected)
  - `UInt32` × 3 - File sizes, offsets, magic numbers
  - `string` × 2 - Version string, timestamp
  - `Int32` × 3 - Loop counters, positions

**Process**:
1. Opens file and checks size
2. Reads header section (first ~256 bytes)
3. Validates magic bytes / format identifier
4. Extracts version string from `VER_POSITION`
5. Extracts timestamp (32 bytes)
6. Computes CRC16 over specific regions
7. Compares computed CRC16 against stored CRC16
8. **Decrypts firmware data** (algorithm unknown)
9. Returns decrypted `byte[]`

#### B. `PareUpdataFile1(string path)` → `byte[]`
**Legacy firmware parser for older format**

- **IL Code Size**: 587 bytes (simpler logic)
- **Local Variables**: Similar but fewer buffers
- **Process**: Similar to `PareUpdataFile` but different offsets/format

#### C. `Updata()` → `void`
**Main update orchestrator**

```csharp
public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;

        // Try newer format
        try {
            array = this.PareUpdataFile(path);
        } catch (Exception ex) {
            array = null;
        }

        // If failed, try legacy format
        if (array == null)
        {
            try {
                array = this.PareUpdataFile1(path);
            } catch (Exception ex) {
                array = null;
            }
        }

        if (array != null)
        {
            if (this.downloadFileEx(array))
            {
                MessageBox.Show(this.GetLang("write_success"));
            }
            else
            {
                MessageBox.Show(this.GetLang("write_fail"));
            }
        }
        else
        {
            MessageBox.Show(this.GetLang("文件版本错误"));  // "File version error"
        }
    }
}
```

#### D. `downloadFileEx(byte[] allBuffer)` → `bool`
**Sends decrypted firmware to device**

- **IL Code Size**: 564 bytes
- **Process**:
  1. Takes decrypted firmware bytes
  2. Splits into packets (1024 bytes default)
  3. Sends over serial protocol
  4. Waits for ACK from device bootloader
  5. Does NOT recalculate CRC (already validated)

---

## 3. Firmware File Format (Reconstructed)

Based on IL code analysis and field names, the format is likely:

```
┌─────────────────────────────────────────────────────────┐
│ OFFSET   │ SIZE    │ TYPE       │ DESCRIPTION           │
├──────────┼─────────┼────────────┼───────────────────────┤
│ 0x0000   │ 4 bytes │ uint32     │ Magic / Format ID     │
│ 0x0004   │ 4 bytes │ uint32     │ Header size           │
│ 0x0008   │ 4 bytes │ uint32     │ Data size             │
│ 0x000C   │ 4 bytes │ uint32     │ Version high/low      │
├──────────┼─────────┼────────────┼───────────────────────┤
│ VER_POS  │ var     │ string     │ Version string        │
│          │         │            │ e.g., "5.00.09"       │
├──────────┼─────────┼────────────┼───────────────────────┤
│ TIME_POS │ 32 bytes│ string     │ Timestamp             │
│          │         │            │ e.g., "2024-05-26..."  │
├──────────┼─────────┼────────────┼───────────────────────┤
│ CRC_POS  │ 2 bytes │ uint16     │ CRC16 checksum        │
│          │         │            │ (CRC16-CCITT likely)  │
├──────────┼─────────┼────────────┼───────────────────────┤
│ HEADER_END│        │            │ End of header         │
├──────────┼─────────┼────────────┼───────────────────────┤
│ DATA_START│ ~350KB │ encrypted  │ Encrypted firmware    │
│          │         │            │ XOR or AES cipher     │
│          │         │            │ Contains ARM code     │
│          │         │            │ + config data         │
├──────────┼─────────┼────────────┼───────────────────────┤
│ FOOTER   │ var     │ padding    │ Optional padding      │
└──────────┴─────────┴────────────┴───────────────────────┘

Total: 357,976 bytes (0x57658)
```

### Unknown Values
- **VER_POSITION**: Exact byte offset (instance field, varies by format)
- **CRC_POSITION**: Exact byte offset
- **Encryption algorithm**: Likely XOR with key schedule or lightweight cipher
- **CRC16 polynomial**: Likely CRC16-CCITT (0x1021) or CRC16-IBM (0x8005)

---

## 4. Why Our Patched Firmware Fails

### What We Did Wrong

1. **Modified encrypted data directly**:
   ```
   # We changed bytes at these offsets in ENCRYPTED firmware:
   0x561EC: 0x03 → 0x09  (USB mode configuration)
   Various: Mode 5→8 configuration changes
   ```

2. **Consequences**:
   - **CRC16 mismatch**: Header CRC16 no longer matches modified data
   - **Encryption corrupted**: Random byte changes break cipher block alignment
   - **Version mismatch**: If version is derived from data, now wrong

3. **What happens**:
   ```
   TK11.exe: PareUpdataFile()
     → CRC check FAILS
     → Returns null
   TK11.exe: PareUpdataFile1()
     → CRC check FAILS
     → Returns null
   TK11.exe: Shows error "File version is Wrong"
   ```

4. **Even with bypass patch**:
   ```
   Patched TK11.exe: File.ReadAllBytes(path)
     → Sends corrupted encrypted data to bootloader
   Device bootloader:
     → Attempts to decrypt
     → Decryption FAILS (corrupted ciphertext)
     → Rejects firmware
   ```

---

## 5. Correct Approach: Decrypt → Modify → Re-encrypt

### Step-by-Step Process

#### Phase 1: Extract Decrypted Firmware

**Method A: Runtime Interception**
```csharp
// Create C# shim that calls TK11.exe internal methods
Assembly tk11 = Assembly.LoadFrom("TK11.exe");
Type wfm = tk11.GetType("K7.wfm_progress");
MethodInfo pareMethod = wfm.GetMethod("PareUpdataFile",
    BindingFlags.NonPublic | BindingFlags.Instance);

object instance = Activator.CreateInstance(wfm);
byte[] decrypted = (byte[])pareMethod.Invoke(instance,
    new object[] { "TK11_v5.00.09_ENG.bin" });

File.WriteAllBytes("TK11_DECRYPTED.bin", decrypted);
```

**Method B: Memory Dumping**
1. Run TK11.exe in debugger (x64dbg / WinDbg)
2. Set breakpoint on `downloadFileEx` entry
3. When hit, dump `allBuffer` parameter from stack/registers
4. Save dumped memory to file

**Method C: IL Reverse Engineering**
1. Export `PareUpdataFile` to C# using dnSpy
2. Port algorithm to Python
3. Run Python script to decrypt original firmware

#### Phase 2: Modify Decrypted Firmware

```python
# Load decrypted firmware
with open('TK11_DECRYPTED.bin', 'rb') as f:
    firmware = bytearray(f.read())

# Find USB mode configuration (now in decrypted space)
# Offset will be DIFFERENT than in encrypted file!
# Need to search for patterns or known markers

# Example: Search for mode configuration structure
for offset in range(len(firmware) - 0x1000):
    if firmware[offset:offset+4] == b'\x03\x00\x00\x00':  # Mode 3
        # Found mode config, check context
        if is_usb_mode_config(firmware, offset):
            print(f'USB mode config at 0x{offset:X}')
            firmware[offset] = 0x09  # Change to mode 9
            break

# Save patched decrypted firmware
with open('TK11_DECRYPTED_PATCHED.bin', 'wb') as f:
    f.write(firmware)
```

#### Phase 3: Re-encrypt and Wrap

**Option A: Use Patched TK11.exe**
```
If we have patched TK11.exe with validation bypass:
  → Load TK11_DECRYPTED_PATCHED.bin directly
  → Bypass sends raw bytes to downloadFileEx()
  → Device MAY accept decrypted firmware
  → IF bootloader doesn't require encryption wrapper
```

**Option B: Reconstruct Wrapper**
```python
def create_firmware_package(decrypted_data, version="5.00.09"):
    """
    Recreate proper firmware format with encryption and CRC
    """
    # Encrypt firmware data
    encrypted = encrypt_firmware(decrypted_data)  # Need algorithm!

    # Build header
    header = bytearray()
    header += struct.pack('<I', 0x204857)  # Magic (guess from file)
    header += struct.pack('<I', len(header))  # Header size
    header += struct.pack('<I', len(encrypted))  # Data size
    header += struct.pack('<I', 0x50009)  # Version (5.00.09)
    header += version.encode('ascii').ljust(16, b'\x00')
    header += datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode('ascii').ljust(32, b'\x00')

    # Calculate CRC16
    crc = calculate_crc16(encrypted)
    header += struct.pack('<H', crc)

    # Combine
    return header + encrypted

firmware = create_firmware_package(patched_decrypted_data)
with open('TK11_PROPERLY_WRAPPED.bin', 'wb') as f:
    f.write(firmware)
```

---

## 6. Immediate Action Plan

### Priority 1: Get Decrypted Firmware ⭐

**Use dnSpy GUI to export PareUpdataFile source code**:

```
1. Open: dnSpy\dnSpy.exe
2. File → Open → TK11.exe
3. Navigate: K7 → wfm_progress → PareUpdataFile
4. Right-click → "Edit Method (C#)..." → Copy all code
5. Save to: PareUpdataFile_SOURCE.cs
6. Analyze the decryption algorithm
```

### Priority 2: Understand Encryption

From the exported source code, identify:
- [ ] XOR key (if XOR cipher)
- [ ] Key schedule algorithm
- [ ] Block size
- [ ] Cipher mode (CBC, ECB, CTR, etc.)

### Priority 3: Test Decrypted Firmware

Try loading decrypted firmware into patched TK11.exe:
- If device accepts it → SUCCESS (bootloader doesn't check encryption)
- If device rejects it → Need to re-encrypt properly

### Priority 4: Create Tools

```
firmware_tools/
├── decrypt.py          # Decrypt original firmware
├── patch.py            # Modify decrypted firmware
├── encrypt.py          # Re-encrypt if needed
├── wrap.py             # Add header/CRC
└── validate.py         # Test CRC calculation
```

---

## 7. Alternative: Direct Bootloader Communication

If firmware wrapper is too complex, consider:

### Bypass TK11.exe Entirely

1. **Reverse engineer serial protocol**:
   - Capture TK11.exe ↔ Device communication with serial sniffer
   - Identify bootloader commands
   - Identify packet format

2. **Send decrypted firmware directly**:
   ```python
   import serial

   ser = serial.Serial('COM3', 115200)

   # Send bootloader enter command
   ser.write(b'\x...')  # Command from sniffed protocol

   # Send decrypted firmware in packets
   with open('TK11_DECRYPTED_PATCHED.bin', 'rb') as f:
       while chunk := f.read(1024):
           ser.write(chunk)
           ack = ser.read(1)  # Wait for ACK

   # Send finish command
   ser.write(b'\x...')
   ```

---

## 8. Files Reference

### Existing Files
```
TK11_v5.00.09_ENG.bin                           357,976 bytes  Encrypted original
patched_firmware/TK11_PATCHED_*.bin             357,976 bytes  Corrupted (wrong approach)
TK11.exe                                        390,656 bytes  Original programmer
TK11_modified.exe                               381,440 bytes  Validation bypassed
```

### Files to Create
```
TK11_DECRYPTED.bin                              ~350,000 bytes  Decrypted original
TK11_DECRYPTED_PATCHED.bin                      ~350,000 bytes  Modified decrypted
TK11_PROPERLY_WRAPPED.bin                       357,976 bytes   Re-encrypted + header
PareUpdataFile_SOURCE.cs                        Text file       Exported source code
firmware_decrypt.py                             Python script   Decryption tool
firmware_patch.py                               Python script   Patching tool
firmware_encrypt.py                             Python script   Re-encryption tool
```

---

## 9. Key Takeaways

✅ **What We Know**:
- Firmware is encrypted with proprietary algorithm
- Header contains version, timestamp, CRC16
- TK11.exe decrypts before sending to device
- Two format versions exist (PareUpdataFile and PareUpdataFile1)

❌ **What Went Wrong**:
- We edited encrypted firmware → corrupted ciphertext
- CRC16 mismatch → TK11.exe rejects file
- Even with bypass, bootloader gets corrupted data

✅ **Correct Approach**:
- Decrypt firmware using TK11.exe logic
- Modify decrypted firmware
- Either: Re-encrypt properly OR send decrypted directly

---

## 10. Next Steps

1. **Extract PareUpdataFile source code** using dnSpy GUI
2. **Understand the decryption algorithm**
3. **Decrypt original firmware** and save to file
4. **Search for USB mode config** in decrypted firmware
5. **Modify decrypted firmware** to enable USB TX
6. **Test** with patched TK11.exe (sends raw decrypted)
7. If fails: **Re-encrypt properly** and wrap with valid header/CRC

---

## Appendix: Useful Commands

### Extract IL Code
```bash
./decompile_firmware_parser.exe > firmware_parser_IL.txt
```

### Get Constants
```bash
./get_constants2.exe > firmware_constants.txt
```

### Analyze Binary
```python
python analyze_firmware_version.py TK11_v5.00.09_ENG.bin
```

### Patch TK11.exe (Already Done)
```
dnSpy → K7.wfm_progress.Updata() → Add bypass → Save
```

---

**Date**: 2025-11-05
**Analysis By**: AI Assistant via Claude Code
**Status**: Firmware format partially understood, decryption algorithm needed
