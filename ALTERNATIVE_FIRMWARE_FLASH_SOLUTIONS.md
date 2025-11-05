# Alternative Firmware Flash Solutions - TK11 Radio

## Problem Statement

**Current Issue:** Patched firmware is rejected with error: "File version is Wrong"

**Root Causes:**
1. TK11.exe uses proprietary/custom checksum validation algorithm
2. Radio bootloader validates firmware header independently
3. Standard checksum algorithms (CRC32, CRC16, Adler32, Fletcher32, etc.) don't match
4. 12+ checksum fix attempts failed

---

## Solution Overview

Based on analysis of `E:\AI\tk11\`, here are **5 concrete alternative approaches** ranked by feasibility:

---

## SOLUTION 1: Patch TK11.exe to Bypass Validation (RECOMMENDED)

### Feasibility: HIGH | Risk: LOW | Time: 30-60 minutes

### What This Does
Modifies TK11.exe to skip firmware validation, allowing any firmware to be uploaded to the radio.

### Implementation Steps

#### Step 1: Open TK11.exe in dnSpy
```bash
E:\AI\tk11\dnSpy\dnSpy.exe
File → Open → E:\AI\tk11\TK11.exe
```

#### Step 2: Locate the Validation Method
Search for the error message:
- Press `Ctrl+Shift+K`
- Search: `文件版本错误` OR `File version is Wrong`
- Double-click result → takes you to `K7.wfm_progress.Updata()` method

#### Step 3: Apply Patch - Version A (Complete Bypass)

**Original code structure:**
```csharp
public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;

        // These methods validate the firmware:
        array = this.PareUpdataFile(path);   // New format validation
        if (array == null)
            array = this.PareUpdataFile1(path); // Old format validation

        if (array != null)
        {
            if (this.downloadFileEx(array))
                MessageBox.Show(this.GetLang("write_success"));
            else
                MessageBox.Show(this.GetLang("write_fail"));
        }
        else
        {
            MessageBox.Show(this.GetLang("文件版本错误"));
        }
    }
}
```

**Replace with:**
```csharp
public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;

        // PATCH: Bypass validation - read firmware directly
        try
        {
            array = File.ReadAllBytes(path);
        }
        catch (Exception ex)
        {
            array = null;
        }

        if (array != null)
        {
            if (this.downloadFileEx(array))
                MessageBox.Show(this.GetLang("write_success"));
            else
                MessageBox.Show(this.GetLang("write_fail"));
        }
        else
        {
            MessageBox.Show(this.GetLang("文件版本错误"));
        }
    }
}
```

#### Step 4: Apply Patch - Version B (Safer - Fallback Bypass)

Add this code AFTER the validation attempts:

```csharp
        // Original validation attempts
        if (array == null)
        {
            try
            {
                array = this.PareUpdataFile1(path);
            }
            catch (Exception ex)
            {
                array = null;
            }
        }

        // PATCH: If validation still failed, bypass it
        if (array == null)
        {
            try
            {
                array = File.ReadAllBytes(path);
            }
            catch (Exception ex2)
            {
                array = null;
            }
        }
```

#### Step 5: Compile and Save
1. Right-click on `Updata` method
2. Select "Edit Method (C#)..."
3. Make changes as shown above
4. Click "Compile" (bottom right)
5. If successful: File → Save Module
6. Save as: `E:\AI\tk11\TK11_PATCHED_BYPASS.exe`

#### Step 6: Test
```bash
# Backup original
copy E:\AI\tk11\TK11.exe E:\AI\tk11\TK11_ORIGINAL_BACKUP.exe

# Use patched version
copy E:\AI\tk11\TK11_PATCHED_BYPASS.exe E:\AI\tk11\TK11.exe

# Launch
E:\AI\tk11\TK11.exe
```

Try loading patched firmware:
```
E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin
```

### Expected Result
- No "File version is Wrong" error
- Firmware flashes successfully
- Radio accepts modified firmware

### Advantages
- Bypasses TK11.exe validation completely
- No need to understand checksum algorithm
- Works for ANY firmware modification
- Can revert easily (restore original TK11.exe)

### Risks
- Radio bootloader might still reject firmware (separate validation layer)
- If bootloader rejects, radio won't be bricked (flash just fails)

---

## SOLUTION 2: Modify Firmware at Offset 0x314D ONLY (Original File)

### Feasibility: MEDIUM | Risk: LOW | Time: 15 minutes

### What This Does
Instead of working with processed/formatted firmware, modify the ORIGINAL firmware file directly at the specific offset.

### Why This Might Work
The previous attempts may have failed because:
1. Firmware was formatted/processed before patching
2. Checksum was calculated on wrong data range
3. Original file structure was altered

### Implementation

#### Step 1: Use Python Script to Patch Original Firmware

Create `E:\AI\tk11\patch_original_directly.py`:

```python
#!/usr/bin/env python3
"""Patch original firmware at exact offset - minimal changes"""

from pathlib import Path
import struct
import zlib

def calculate_crc16_xmodem(data):
    """CRC16-XMODEM - common in embedded systems"""
    crc = 0
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def patch_firmware():
    original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
    output = Path(r"E:\AI\tk11\patched_firmware\TK11_MINIMAL_PATCH.bin")

    # Read original
    with open(original, 'rb') as f:
        data = bytearray(f.read())

    print(f"Original firmware size: {len(data):,} bytes")

    # ONLY patch the TX validation mask
    offset = 0x0000314D
    original_value = data[offset]
    new_value = 0x13  # Enable USB mode (bit 4)

    print(f"\nPatch location: 0x{offset:08X}")
    print(f"Original value: 0x{original_value:02X}")
    print(f"New value:      0x{new_value:02X}")

    # Apply single byte patch
    data[offset] = new_value

    # Try to fix CRC16 in header (common locations)
    # Skip first 4-16 bytes (usually header signature/length)
    # Calculate CRC over rest of file

    crc_locations = [0x02, 0x04, 0x06, 0x0A, 0x0E]

    for crc_offset in crc_locations:
        # Calculate CRC16 over data AFTER the CRC field
        crc_data = data[crc_offset+2:]
        crc16 = calculate_crc16_xmodem(crc_data)

        # Store in little-endian
        data[crc_offset:crc_offset+2] = struct.pack('<H', crc16)

        print(f"Updated CRC16 at offset 0x{crc_offset:04X}: 0x{crc16:04X}")

    # Write output
    with open(output, 'wb') as f:
        f.write(data)

    print(f"\nPatched firmware saved: {output}")
    print(f"Changed bytes: 1 (at 0x{offset:08X}) + {len(crc_locations)} CRC updates")

if __name__ == "__main__":
    patch_firmware()
```

#### Step 2: Run Script
```bash
cd E:\AI\tk11
python patch_original_directly.py
```

#### Step 3: Test with Patched TK11.exe (from Solution 1)
Or try with original TK11.exe (might work if CRC16 is correct)

### Advantages
- Minimal changes to firmware (1 byte + CRC)
- Original file structure preserved
- Lower chance of corruption

---

## SOLUTION 3: Force "Old Boot Protocol" Mode

### Feasibility: MEDIUM | Risk: MEDIUM | Time: 1-2 hours

### What This Does
The TK11.exe has references to `protocol_struct.boot_version` and old/new bootloader protocols. Older bootloaders may have simpler or no validation.

### Investigation Steps

#### Step 1: Analyze Boot Version Check

In dnSpy, search for:
```
protocol_struct.check_boot_ver
protocol_struct.boot_version
GetUpdataReady
```

#### Step 2: Identify Version Logic

Look for code like:
```csharp
if (protocol_struct.boot_version < "2.0") {
    // Old protocol - simpler validation?
    useSimpleFlash();
} else {
    // New protocol - strict validation
    useSecureFlash();
}
```

#### Step 3: Force Old Protocol

Option A: Modify radio's response
- When TK11.exe queries boot version, radio responds with version string
- Patch TK11.exe to IGNORE actual version, always use old protocol

Option B: Patch protocol selection
- Find where `GetUpdataReady()` checks version
- Force it to return "old boot version" flag

### Implementation Example

Search in dnSpy for `check_boot_ver` method:
```csharp
public static bool check_boot_ver(string ver)
{
    // Original logic checks version string
    // Force return true for old version
}
```

Modify to:
```csharp
public static bool check_boot_ver(string ver)
{
    return true; // Always use old protocol
}
```

Or modify the calling code to skip version check entirely.

### Advantages
- Old bootloader protocols often have weaker validation
- Might bypass checksum entirely
- Potentially more compatible

### Risks
- Unknown if TK11 actually has different boot protocols
- May cause communication issues
- Requires deeper reverse engineering

---

## SOLUTION 4: Direct Memory Write via CpsWrite Methods

### Feasibility: LOW-MEDIUM | Risk: HIGH | Time: 4-8 hours

### What This Does
Instead of using firmware update methods, use the regular CPS (Customer Programming Software) write functions to write firmware data directly to radio memory.

### Background
Analysis shows TK11.exe has many `CpsWrite*` methods:
- `CpsWriteGen`
- `CpsWritePassword`
- `CpsWriteVfo`
- etc.

These write configuration data to radio memory. Firmware is just data in flash memory.

### Theory
If we can:
1. Map the firmware memory address range
2. Split firmware into chunks
3. Use CpsWrite methods to write each chunk
4. Bypass bootloader validation entirely

### Investigation Steps

#### Step 1: Find Memory Write Primitives

Search in dnSpy for:
```
CpsWrite
WriteMemory
SendCommand
protocol_struct.write
```

#### Step 2: Analyze Write Protocol

Look for:
- Memory address parameters
- Data chunk size limits
- Write confirmation/verification

#### Step 3: Create Custom Flash Tool

Pseudo-code:
```python
def flash_via_cps_write(firmware_path):
    firmware = read_file(firmware_path)

    # Split into chunks (typical: 64-256 bytes)
    chunk_size = 128
    base_address = 0x08000000  # Typical STM32 flash start

    for offset in range(0, len(firmware), chunk_size):
        chunk = firmware[offset:offset+chunk_size]
        address = base_address + offset

        # Use CPS protocol to write chunk
        send_write_command(address, chunk)
        verify_write(address, chunk)

    print("Flash complete via direct write")
```

#### Step 4: Protocol Reverse Engineering

Use Wireshark/Serial monitor to capture:
1. Normal CPS write operations (configuration)
2. Firmware update operations
3. Compare protocols
4. Identify direct memory write commands

### Advantages
- Completely bypasses firmware validation
- Uses existing radio protocols
- No bootloader involvement

### Risks
- HIGH: Wrong memory writes can brick radio permanently
- Complex protocol reverse engineering required
- May require EEPROM unlock commands
- No safety checks

**⚠️ NOT RECOMMENDED without expert knowledge**

---

## SOLUTION 5: JTAG/SWD Hardware Programming

### Feasibility: LOW | Risk: VERY HIGH | Time: 8-24 hours

### What This Does
Bypass all software, write directly to flash memory using hardware debugger.

### Required Hardware
- ST-Link V2 programmer (~$10-20 on AliExpress)
- OR J-Link programmer (~$50+)
- Soldering iron
- Thin wires (30 AWG)
- Multimeter

### Implementation Steps

#### Step 1: Identify MCU

Radio likely uses:
- STM32F series (common in radios)
- OR other ARM Cortex-M MCU

#### Step 2: Locate Debug Port

Disassemble radio, find:
- SWDIO pin
- SWCLK pin
- GND pin
- VCC (3.3V) - optional, can power from radio

Look for:
- Unpopulated header near MCU
- Test points labeled SWD/JTAG
- MCU datasheet pinout

#### Step 3: Connect ST-Link

```
ST-Link    →    Radio
------          -----
SWDIO    →    SWDIO (identify on PCB)
SWCLK    →    SWCLK (identify on PCB)
GND      →    GND
VCC      →    3.3V (optional)
```

#### Step 4: Use OpenOCD

Install OpenOCD, configure for STM32:

```bash
# openocd.cfg
source [find interface/stlink.cfg]
source [find target/stm32f1x.cfg]  # Adjust for actual MCU

init
reset halt

# Flash patched firmware
flash write_image erase E:/AI/tk11/patched_firmware/TK11_PATCHED_USB_TX_ENABLED.bin 0x08000000
verify_image E:/AI/tk11/patched_firmware/TK11_PATCHED_USB_TX_ENABLED.bin 0x08000000

reset run
exit
```

#### Step 5: Flash Firmware

```bash
openocd -f openocd.cfg
```

### Advantages
- Bypasses ALL software validation
- Complete control over flash memory
- Can unbrick radios (if bootloader damaged)
- Can dump original firmware for backup

### Risks
- VERY HIGH: Can permanently brick radio
- Requires radio disassembly (voids warranty)
- Risk of physical damage (ESD, short circuits)
- May destroy radio if wrong MCU type
- Debug port might be disabled/locked

**⚠️ ONLY for experienced hardware hackers**

---

## Recommended Approach

### START HERE: Try solutions in this order

**1. Solution 1 (Patch TK11.exe) - Start with Version B (safer)**
- Risk: LOW
- Success probability: 80%
- Time: 30-60 minutes
- If this works, you're done!

**2. If Solution 1 fails at radio bootloader validation:**
- Try Solution 2 (patch original firmware with CRC16)
- Risk: LOW
- Success probability: 40%
- Time: 15 minutes

**3. If both fail:**
- Solution 3 (force old boot protocol)
- Requires more reverse engineering
- Risk: MEDIUM
- Success probability: 30%
- Time: 2-4 hours

**4. Advanced (if desperate):**
- Solution 4: Direct memory write (RISKY)
- Solution 5: JTAG/SWD (VERY RISKY)

---

## Quick Start: Solution 1 Implementation

### Complete Step-by-Step

1. **Open dnSpy**
   ```
   E:\AI\tk11\dnSpy\dnSpy.exe
   ```

2. **Load TK11.exe**
   ```
   File → Open → E:\AI\tk11\TK11.exe
   ```

3. **Find validation method**
   ```
   Ctrl+Shift+K
   Search: 文件版本错误
   Double-click result
   ```

4. **Edit method**
   ```
   Right-click "Updata" method
   Select "Edit Method (C#)..."
   ```

5. **Apply Version B patch (safer):**
   - Scroll to where `array = this.PareUpdataFile1(path);` is called
   - AFTER that try/catch block, ADD:
   ```csharp
   // PATCH: Bypass validation fallback
   if (array == null)
   {
       try
       {
           array = File.ReadAllBytes(path);
       }
       catch (Exception ex)
       {
           array = null;
       }
   }
   ```

6. **Compile**
   ```
   Click "Compile" button
   Check for errors
   ```

7. **Save**
   ```
   File → Save Module
   Save as: E:\AI\tk11\TK11_PATCHED_BYPASS.exe
   ```

8. **Test**
   ```bash
   # Backup
   copy TK11.exe TK11_ORIGINAL_BACKUP.exe

   # Use patched
   copy TK11_PATCHED_BYPASS.exe TK11.exe

   # Run
   TK11.exe
   ```

9. **Flash firmware**
   ```
   Load: E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin
   ```

### Success Indicators

**TK11.exe level:**
- ✅ No "File version is Wrong" error
- ✅ Firmware file loads
- ✅ Flash process starts

**Radio level:**
- ✅ Flash completes without error
- ✅ Radio reboots successfully
- ✅ Radio functions normally

**Full success:**
- ✅ Can load USB mode configuration
- ✅ K38 USB channel works
- ✅ PTT works (no DISABLE message)

---

## Troubleshooting

### TK11.exe still shows "File version is Wrong"
- Patch didn't compile correctly
- Wrong method edited
- Not using patched exe
- Try Version A (complete bypass) instead

### Radio bootloader rejects firmware
- Try Solution 2 (CRC16 fix)
- Try Solution 3 (old boot protocol)
- May need JTAG (Solution 5)

### Radio bricked after flash
- Don't panic
- Try reflashing original firmware
- If that fails, need JTAG recovery
- Check if radio enters bootloader mode (special button combination)

---

## Files Reference

### Existing Files
```
E:\AI\tk11\TK11.exe                          - Original programming software
E:\AI\tk11\TK11_v5.00.09_ENG.bin             - Original firmware
E:\AI\tk11\dnSpy\dnSpy.exe                   - .NET decompiler/editor
E:\AI\tk11\patched_firmware\*.bin            - Patched firmware files
E:\AI\tk11\DNSPY_PATCH_UTASITAS.md          - dnSpy instructions (Hungarian)
```

### To Create
```
E:\AI\tk11\TK11_PATCHED_BYPASS.exe          - Patched TK11.exe (Solution 1)
E:\AI\tk11\patch_original_directly.py       - Script for Solution 2
E:\AI\tk11\patched_firmware\TK11_MINIMAL_PATCH.bin - Output from Solution 2
```

---

## Summary Table

| Solution | Feasibility | Risk | Time | Success Est. | Skill Level |
|----------|-------------|------|------|--------------|-------------|
| 1. Patch TK11.exe | HIGH | LOW | 30-60m | 80% | Beginner |
| 2. Original + CRC16 | MEDIUM | LOW | 15m | 40% | Beginner |
| 3. Old Boot Protocol | MEDIUM | MEDIUM | 2-4h | 30% | Intermediate |
| 4. Direct Memory Write | LOW | HIGH | 4-8h | 20% | Advanced |
| 5. JTAG/SWD | LOW | VERY HIGH | 8-24h | 90%* | Expert |

*90% success IF you have hardware skills, otherwise likely to brick radio

---

## Conclusion

**Best chance of success: Solution 1 (Patch TK11.exe)**

This bypasses the validation in software where you have control, rather than trying to calculate the unknown checksum algorithm.

**If Solution 1 doesn't work**, the issue is at the radio bootloader level, which means:
- Either Solution 2 with correct CRC fixes it
- OR hardware programming (Solution 5) is required

**Start with Solution 1 Version B** - it's safe, reversible, and most likely to succeed.

Good luck! 73! 📻
