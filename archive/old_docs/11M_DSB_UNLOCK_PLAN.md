# 11-Meter Band DSB Mode Unlock Plan
## Comprehensive Strategy for Enabling DSB Transmission on CB Frequencies

**Target:** TK11 Radio
**Objective:** Enable DSB (Double Sideband) transmission on 11-meter band (26.965 - 27.405 MHz)
**Approach:** Selective unlock - ONLY 11m band, not all frequencies
**Date:** 2025-10-29

---

## Executive Summary

This document provides a complete strategy to enable DSB (Double Sideband) transmission on the 11-meter CB band (26.965-27.405 MHz) for the TK11 radio. Based on reverse engineering of TK11.dat and firmware analysis, we have identified the critical bytes controlling transmission permissions and modulation modes.

**Key Finding:** There are currently NO CB channels programmed in TK11.dat. We must CREATE them with proper DSB mode settings.

---

## 1. Current State Analysis

### 1.1 Existing TX Unlock Knowledge

From TX_UNLOCK_REPORT.md, we know:

- **Byte 22 (TX Permit Flag):**
  - `0xFF` = TX ENABLED
  - `0x00` = TX DISABLED
  - Location: Offset +0x16 in each 64-byte channel record

- **Channel Record Structure:**
  - Size: 64 bytes per channel
  - Total capacity: 13,760 channel records
  - Frequency encoding: 32-bit little-endian, in Hz

### 1.2 Modulation Mode Discovery

**CRITICAL FINDING:** Byte 23 is the PRIMARY mode selector

Analysis of existing channels revealed:
- **K38 USB** (2.7385 MHz): Byte 23 = `0x04` → USB mode
- **K14 FM** (2.7125 MHz): Byte 23 = `0x02` → FM mode

**Confirmed Mode Values:**
```
Byte 23:
  0x02 = FM (Frequency Modulation)
  0x04 = USB (Upper Side Band)
```

**Hypothesized Values for DSB:**
```
  0x05 = DSB (Most likely - sequential)
  0x06 = DSB variant / LSB
  0x08 = DSB (if bit-flag based)
  0x01 = AM (for comparison testing)
  0x03 = LSB (for comparison testing)
```

### 1.3 Current 11-Meter Band Status

**Scan Results:** NO CB channels currently programmed in TK11.dat

Frequency bands present:
- HF: 1.8-22.9 MHz (20 channels) - but no CB range
- VHF Low: 35-76 MHz (30 channels)
- FM Broadcast: 100 MHz (2 channels)
- UHF: Various bands (33 channels)

**Action Required:** Must CREATE CB channels from scratch

---

## 2. 11-Meter Band Channel Specifications

### 2.1 CB Channel Definitions

Standard CB channels (USA/International):

| Channel | Frequency (MHz) | Notes |
|---------|----------------|-------|
| 1 | 26.965 | Start of band |
| 4 | 27.005 | |
| 9 | 27.065 | Emergency channel (USA) |
| 19 | 27.185 | **Popular calling channel** |
| 38 | 27.385 | |
| 40 | 27.405 | End of band |

Total: 40 channels spanning 26.965 - 27.405 MHz

### 2.2 Channel Offsets in TK11.dat

Since no CB channels exist, we will use EMPTY channel slots:
- Empty slots identified: 980 channels (filled with 0xFF)
- Strategy: Populate first 40 empty slots with CB channels

**Channel Record Calculation:**
```
Record N starts at offset: N × 64 (decimal) or N × 0x40 (hex)
```

---

## 3. Byte Modification Strategy

### 3.1 64-Byte Channel Record Layout

Complete map of bytes that must be set:

```
Offset | Bytes | Field                    | Value for CB DSB
-------|-------|--------------------------|------------------
0x00   | 4     | RX Frequency (Hz)        | CB freq (e.g., 27185000 for CH19)
0x04   | 4     | TX Frequency             | 0x00000000 (simplex)
0x08   | 2     | RX CTCSS/DCS             | 0x0000 (none)
0x0A   | 2     | TX CTCSS/DCS             | 0x0000 (none)
0x0C   | 4     | Unknown flags            | 0x00000000
0x10   | 1     | Power level              | 0x02 (standard)
0x11   | 1     | Bandwidth                | 0x00 (standard)
0x12   | 1     | Modulation subtype       | 0x00 (default)
0x13   | 1     | Scrambler                | 0x00 (off)
0x14   | 1     | Byte 20                  | 0x00
0x15   | 1     | Byte 21                  | 0x03 (observed pattern)
0x16   | 1     | **TX PERMIT (CRITICAL)** | **0xFF (ENABLED)**
0x17   | 1     | **MODE SELECTOR**        | **0x05 (DSB hypothesis)**
0x18   | 16    | Channel name (ASCII)     | "CB-19\0\0..." (null-padded)
0x28   | 8     | Additional settings      | 0x0000000000000000
0x30   | 16    | Reserved                 | 0x00... (all zeros)
```

### 3.2 Critical Bytes Summary

**MUST SET:**
1. **Bytes 0-3:** Frequency in Hz, little-endian (e.g., `0x019F3748` = 27,185,000)
2. **Byte 22 (0x16):** TX Permit = `0xFF` (enables transmission)
3. **Byte 23 (0x17):** Mode = `0x05` (hypothesized DSB value)

**SHOULD SET:**
4. **Bytes 24-39:** Channel name (e.g., "CB-19")
5. **Byte 16:** Power level = `0x02`
6. **Byte 21:** = `0x03` (observed in USB channel)

---

## 4. DSB Mode Testing Strategy

### 4.1 Test Approach

Since DSB mode value is unknown, we use iterative testing:

**Phase 1: Single Channel Test**
- Create test versions with ONLY CB Channel 19 (27.185 MHz)
- Test mode byte values: 0x05, 0x06, 0x08, 0x01, 0x03
- Monitor with spectrum analyzer
- Identify correct DSB mode value

**Phase 2: Full Band Deployment**
- Once correct mode value confirmed
- Program all 40 CB channels
- Set all to TX enabled (Byte 22 = 0xFF)

### 4.2 Test File Matrix

| File | Mode Byte | Description | Purpose |
|------|-----------|-------------|---------|
| TK11_11M_DSB_MODE_05.dat | 0x05 | DSB hypothesis 1 | Most likely - sequential after 0x04 |
| TK11_11M_DSB_MODE_06.dat | 0x06 | DSB hypothesis 2 | Alternate sequential |
| TK11_11M_DSB_MODE_08.dat | 0x08 | DSB hypothesis 3 | Bit-flag pattern (0x04 << 1) |
| TK11_11M_DSB_MODE_01.dat | 0x01 | AM mode test | Comparison baseline |
| TK11_11M_DSB_MODE_03.dat | 0x03 | LSB mode test | Comparison baseline |

### 4.3 Verification Procedure

For each test file:

1. **Upload to Radio**
   - Use TK11 programming software
   - Load modified .dat file
   - Write to radio

2. **Visual Check**
   - Navigate to CB-19 channel on radio
   - Verify frequency shows 27.185 MHz
   - Verify channel name displays "CB-19"

3. **TX Test (with dummy load)**
   - Connect 50Ω dummy load
   - Press PTT button
   - Verify TX LED activates
   - Check no error messages

4. **Spectrum Analysis**
   - Connect to spectrum analyzer or
   - Monitor with second receiver
   - Press PTT and observe:
     - **DSB:** Two sidebands + carrier (3 components)
     - **USB:** Upper sideband only (no carrier)
     - **AM:** Two sidebands + strong carrier
     - **FM:** Wide frequency deviation

5. **Record Results**
   - Document which mode byte produces DSB
   - Update this plan with confirmed value

---

## 5. Implementation Procedures

### 5.1 Method 1: Automated Script (RECOMMENDED)

**Script:** `unlock_11m_dsb.py`

**Usage:**
```bash
cd E:\AI\tk11
python unlock_11m_dsb.py
```

**Menu Options:**
1. Create test versions (5 files with different mode bytes)
2. Create full CB band (40 channels, confirmed mode value)
3. Both

**Output Files:**
- Test versions: `TK11_11M_DSB_MODE_<XX>_<timestamp>.dat`
- Full band: `TK11_CB_FULL_DSB_<timestamp>.dat`
- Backup: `TK11_BACKUP_<timestamp>.dat`

### 5.2 Method 2: Manual Hex Editor

For manual creation of a single CB channel:

**Example: CB Channel 19 at 27.185 MHz**

1. Open TK11.dat in hex editor (HxD, 010 Editor, etc.)

2. Find empty channel slot:
   - Search for `FF FF FF FF FF FF FF FF...` (64 consecutive 0xFF bytes)
   - Note offset (e.g., 0x00010000 = channel 1024)

3. Replace entire 64-byte block with:
```hex
Offset +0x00: 48 37 9F 01  00 00 00 00  00 00 00 00  00 00 00 00
Offset +0x10: 02 00 00 00  00 03 FF 05  43 42 2D 31  39 00 00 00
Offset +0x20: 00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00
Offset +0x30: 00 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00
```

**Breakdown:**
- `48 37 9F 01` = 27,185,000 Hz (little-endian)
- Position +0x16: `FF` = TX enabled
- Position +0x17: `05` = DSB mode (hypothesis)
- Position +0x18-0x1F: `43 42 2D 31 39` = "CB-19" in ASCII

4. Save file as `TK11_CB19_TEST.dat`

### 5.3 Frequency Encoding Reference

Convert MHz to hex bytes (little-endian):

**Formula:**
```python
freq_hz = int(freq_mhz * 1_000_000)
byte0 = freq_hz & 0xFF
byte1 = (freq_hz >> 8) & 0xFF
byte2 = (freq_hz >> 16) & 0xFF
byte3 = (freq_hz >> 24) & 0xFF
```

**Common CB Channels:**
| Channel | MHz | Hex Bytes (LE) |
|---------|-----|----------------|
| 1 | 26.965 | `C8 6A 9B 01` |
| 9 | 27.065 | `E8 A0 9C 01` |
| 19 | 27.185 | `48 37 9F 01` |
| 40 | 27.405 | `88 CD A1 01` |

---

## 6. Alternative Approaches

### 6.1 If DSB Not Supported in Firmware

**Scenario:** None of the test values produce DSB modulation

**Alternative 1: Use AM Mode**
- DSB is essentially AM with both sidebands
- Set Byte 23 to AM mode value
- May need to adjust other parameters

**Alternative 2: Firmware Patch**
- Requires disassembly of TK11_v5.00.09_ENG.bin
- Locate mode handler table in firmware
- Add DSB mode entry or modify existing mode
- **Complexity:** HIGH - requires firmware reverse engineering

**Alternative 3: Hardware Modification**
- Bypass software mode control
- Direct modulation circuit modification
- **Complexity:** VERY HIGH - requires circuit analysis

### 6.2 If Firmware Patch Required

**Firmware Analysis Locations:**

From firmware scan results:
- AM references: 7 occurrences (0x00003AFB, 0x0000D4DB, etc.)
- FM references: 4 occurrences (0x00010EBA, 0x00012DAB, etc.)
- CW references: 5 occurrences (0x0002E0E0, 0x0002EA5E, etc.)
- CB references: 3 occurrences (0x0000A006, 0x0000EC43, 0x00015C3F)

**Potential Mode Table Locations:**
- Near mode string clusters
- Look for byte sequences: `00 01 02 03 04` (mode indices)
- Analyze function calls from mode selector code

**Tools Required:**
- Ghidra or IDA Pro for disassembly
- Binary diff tool to compare firmware versions
- SPI/JTAG programmer for firmware flashing

---

## 7. Safety and Legal Considerations

### 7.1 Legal Compliance

**United States:**
- CB Radio: FCC Part 95 Rules
- Authorized modes: AM, SSB (USB/LSB)
- Power limits:
  - AM: 4 watts carrier
  - SSB: 12 watts PEP
- License: Not required for CB use
- Frequency range: 26.965-27.405 MHz (40 channels)

**International:**
- Regulations vary by country
- Some countries: Different channel spacing (e.g., CEPT: 40 channels @ 10 kHz spacing)
- Check local regulations before transmitting

**Important:** DSB mode may not be explicitly authorized in all jurisdictions. Verify local regulations.

### 7.2 Technical Safety

**Testing Precautions:**

1. **Use Dummy Load**
   - 50Ω, minimum 10W rating
   - Test all new configurations with dummy load first
   - No antenna during initial testing

2. **Power Monitoring**
   - Use RF power meter
   - Verify output power within legal limits
   - Check for spurious emissions

3. **Spectrum Analysis**
   - Verify clean modulation
   - Check for harmonics
   - Ensure no out-of-band emissions

4. **Low Power Testing**
   - Start with lowest power setting
   - Gradually increase if needed
   - Monitor radio temperature

### 7.3 Data Backup

**CRITICAL:** Always maintain backups

1. **Before ANY modification:**
   ```bash
   cp TK11.dat TK11_BACKUP_ORIGINAL.dat
   ```

2. **Document original state:**
   - Channel list
   - Frequency plan
   - Mode settings

3. **Keep multiple versions:**
   - Original factory file
   - Working configuration
   - Test configurations

---

## 8. Troubleshooting Guide

### 8.1 Common Issues

**Problem:** Radio rejects modified file

**Solutions:**
- Verify file size exactly 880,640 bytes
- Check no corruption during transfer
- Ensure programming software version matches
- Try rebooting radio after upload

---

**Problem:** TX LED doesn't activate

**Solutions:**
- Verify Byte 22 = 0xFF
- Check PTT button functionality
- Verify frequency within radio hardware range
- Test with known-good channel first

---

**Problem:** Wrong modulation mode

**Solutions:**
- Try different Byte 23 values
- Verify Byte 18 is 0x00
- Check Byte 17 (bandwidth) setting
- Compare with working USB channel settings

---

**Problem:** No audio on receive

**Solutions:**
- Verify RX frequency correct
- Check squelch settings (Byte 41)
- Ensure correct mode for received signal
- Test with strong local signal

---

### 8.2 Verification Checklist

After programming, verify:

- [ ] File uploads without errors
- [ ] CB channels appear in channel list
- [ ] Frequency display shows 27.xxx MHz
- [ ] Channel names display correctly
- [ ] PTT activates TX LED
- [ ] Spectrum analyzer shows expected mode
- [ ] Power output within legal limits
- [ ] Receive functionality works
- [ ] No spurious emissions

---

## 9. Channel Modification Table

Complete table for all 40 CB channels:

| CB Ch | Freq (Hz) | Freq Bytes (LE) | Record Offset | Name | Byte 22 | Byte 23 |
|-------|-----------|-----------------|---------------|------|---------|---------|
| 1 | 26965000 | C8 6A 9B 01 | (empty slot 1) | CB-1 | FF | 05 |
| 2 | 26975000 | 18 7B 9B 01 | (empty slot 2) | CB-2 | FF | 05 |
| 3 | 26985000 | 68 8B 9B 01 | (empty slot 3) | CB-3 | FF | 05 |
| 4 | 27005000 | 08 AC 9B 01 | (empty slot 4) | CB-4 | FF | 05 |
| 5 | 27015000 | 58 BC 9B 01 | (empty slot 5) | CB-5 | FF | 05 |
| ... | ... | ... | ... | ... | ... | ... |
| 19 | 27185000 | 48 37 9F 01 | (empty slot 19) | CB-19 | FF | 05 |
| ... | ... | ... | ... | ... | ... | ... |
| 40 | 27405000 | 88 CD A1 01 | (empty slot 40) | CB-40 | FF | 05 |

**Note:** Actual record offsets determined at runtime by script (uses first 40 empty slots)

---

## 10. Step-by-Step Execution Plan

### Phase 1: Preparation (5 minutes)

1. **Backup original file**
   ```bash
   cd E:\AI\tk11
   cp TK11.dat TK11_ORIGINAL_BACKUP.dat
   ```

2. **Verify tools installed**
   - Python 3.x
   - Hex editor (optional, for manual verification)
   - Radio programming software

3. **Review this document**
   - Understand byte layout
   - Note legal warnings
   - Prepare test equipment

### Phase 2: Test File Creation (2 minutes)

1. **Run unlock script**
   ```bash
   python unlock_11m_dsb.py
   ```

2. **Select option 1** (Create test versions)

3. **Verify output files created:**
   - TK11_11M_DSB_MODE_05_*.dat
   - TK11_11M_DSB_MODE_06_*.dat
   - TK11_11M_DSB_MODE_08_*.dat
   - TK11_11M_DSB_MODE_01_*.dat
   - TK11_11M_DSB_MODE_03_*.dat

### Phase 3: Testing (30-60 minutes)

**For EACH test file:**

1. **Upload to radio** (5 min)
   - Open programming software
   - Read current config (backup)
   - Write test file to radio

2. **Verify channel** (2 min)
   - Navigate to CB-19
   - Check frequency: 27.185 MHz
   - Check name: "CB-19"

3. **Dummy load test** (5 min)
   - Connect 50Ω dummy load
   - Press PTT
   - Verify TX LED on
   - No error messages

4. **Spectrum analysis** (10 min)
   - Connect spectrum analyzer OR
   - Monitor with second receiver
   - Key up and observe modulation:
     - Count sidebands
     - Check carrier presence
     - Note bandwidth

5. **Record results** (2 min)
   - Document mode byte value
   - Note modulation type observed
   - Note any anomalies

### Phase 4: Full Deployment (10 minutes)

**After identifying correct DSB mode value:**

1. **Update script** (if needed)
   - Edit unlock_11m_dsb.py
   - Set `mode_value` to confirmed value

2. **Create full CB band file**
   ```bash
   python unlock_11m_dsb.py
   # Select option 2
   ```

3. **Upload to radio**
   - Write TK11_CB_FULL_DSB_*.dat
   - Verify all 40 channels present

4. **Spot check**
   - Test CB-1, CB-19, CB-40
   - Verify TX works on all
   - Confirm mode correct

### Phase 5: Documentation (5 minutes)

1. **Update this plan**
   - Record confirmed mode byte value
   - Note any issues encountered
   - Document final configuration

2. **Label radio**
   - Indicate CB mode enabled
   - Note date of modification

3. **File organization**
   - Keep backup accessible
   - Store test files
   - Archive documentation

---

## 11. Expected Results

### 11.1 Success Criteria

**Configuration File:**
- 40 CB channels added (26.965-27.405 MHz)
- All channels TX enabled (Byte 22 = 0xFF)
- DSB mode set on all (Byte 23 = confirmed value)

**Radio Behavior:**
- All CB channels selectable
- PTT activates transmission
- Correct modulation mode
- Within power limits

**Spectrum Analysis:**
- DSB: Two sidebands + carrier
- Symmetrical spectrum
- Clean modulation
- No spurious emissions

### 11.2 If Unsuccessful

**Scenario 1:** No mode value produces DSB

**Action:** DSB may not be implemented in firmware
- Use AM mode as alternative (closest to DSB)
- Consider firmware patch (advanced)
- Document limitation

**Scenario 2:** Radio rejects channels

**Action:** Frequency range may be hardware-locked
- Check radio specifications
- Verify frequency coverage
- May require hardware modification

**Scenario 3:** TX works but wrong mode

**Action:** Additional bytes may control mode
- Analyze Byte 17, 18, 21
- Compare with other radios
- Test combinations

---

## 12. Python Script Reference

### 12.1 Provided Scripts

**Location:** `E:\AI\tk11\`

1. **unlock_11m_dsb.py** - Main unlock script
   - Creates test versions
   - Creates full CB band
   - Automated channel generation

2. **scan_11m_channels.py** - Analysis tool
   - Scans for existing CB channels
   - Analyzes modulation modes
   - Generates statistics

3. **frequency_scanner.py** - Diagnostic tool
   - Shows all programmed frequencies
   - Identifies empty slots
   - Band distribution analysis

4. **dsb_mode_research.py** - Research tool
   - Searches firmware for mode strings
   - Analyzes mode patterns
   - Generates hypotheses

### 12.2 Script Usage Examples

**Create test files only:**
```bash
python unlock_11m_dsb.py
# Select: 1
```

**Create full 40-channel CB band:**
```bash
python unlock_11m_dsb.py
# Select: 2
```

**Analyze existing channels:**
```bash
python scan_11m_channels.py
```

**Research mode values:**
```bash
python dsb_mode_research.py
```

---

## 13. Firmware Patch Considerations

### 13.1 If Configuration-Level Unlock Insufficient

**Firmware File:** `TK11_v5.00.09_ENG.bin`

**Potential Patch Locations:**

1. **Mode Handler Table**
   - Search near CW/AM/FM references
   - Look for function pointer arrays
   - Add DSB mode entry

2. **Frequency Range Locks**
   - CB references found at: 0x0000A006, 0x0000EC43, 0x00015C3F
   - May contain range restrictions
   - Patch to allow 11m band

3. **TX Permit Logic**
   - May have firmware-level TX restrictions
   - Override with NOP instructions
   - Ensure doesn't brick radio

**Tools:**
- Ghidra (free, recommended)
- IDA Pro (commercial)
- Binary diff tool
- Hex editor

**Procedure:**
1. Load firmware in Ghidra
2. Search for mode string references
3. Analyze surrounding code
4. Identify mode dispatch table
5. Add DSB mode handler
6. Verify checksums
7. Flash modified firmware

**Risk Level:** HIGH
- Can brick radio if done incorrectly
- Requires firmware backup capability
- Test on non-critical radio first

### 13.2 Firmware Patching Script Template

```python
# firmware_patcher.py - TEMPLATE ONLY

def patch_mode_table(firmware_data, offset, new_mode_entry):
    """
    Patch mode handler table in firmware

    Args:
        firmware_data: bytearray of firmware
        offset: Location of mode table
        new_mode_entry: Mode handler struct (8 bytes)
    """
    # Insert new mode entry
    firmware_data[offset:offset+8] = new_mode_entry

    # Recalculate checksum (if needed)
    # ...

    return firmware_data

# USE ONLY IF CONFIGURATION FILE APPROACH FAILS
# EXTREMELY DANGEROUS - CAN BRICK RADIO
```

---

## 14. Summary and Next Steps

### 14.1 What We Know

1. **TX unlock mechanism:** Byte 22 = 0xFF enables transmission ✓
2. **Mode selector:** Byte 23 controls modulation mode ✓
3. **Current state:** No CB channels in TK11.dat ✓
4. **Mode values:** 0x02=FM, 0x04=USB confirmed ✓

### 14.2 What We Need to Determine

1. **DSB mode byte value:** Test 0x05, 0x06, 0x08, or others
2. **Firmware support:** Does radio actually support DSB?
3. **Additional parameters:** Any other bytes affect DSB?

### 14.3 Recommended Action Plan

**IMMEDIATE (Today):**
1. Run `unlock_11m_dsb.py` to create test files
2. Upload first test file (mode 0x05) to radio
3. Test with dummy load and spectrum analyzer
4. Document results

**SHORT TERM (This Week):**
1. Test all mode byte variations
2. Identify correct DSB value (if it exists)
3. Create full 40-channel CB configuration
4. Perform comprehensive testing

**LONG TERM (If Needed):**
1. If DSB not supported: Use AM mode or patch firmware
2. Document final configuration
3. Create user guide for other TK11 users

### 14.4 Final Warnings

⚠️ **LEGAL:** Ensure compliance with local radio regulations

⚠️ **SAFETY:** Always test with dummy load first

⚠️ **BACKUP:** Keep original TK11.dat file safe

⚠️ **EQUIPMENT:** Use spectrum analyzer to verify mode

⚠️ **POWER:** Stay within legal power limits (4W AM, 12W SSB PEP)

---

## 15. References

### 15.1 Internal Documents

- `TX_UNLOCK_REPORT.md` - Original TX unlock analysis
- `detailed_channel_analysis.py` - Channel structure analysis
- Firmware analysis scripts in `E:\AI\tk11\`

### 15.2 Technical Specifications

**CB Radio (USA - FCC Part 95):**
- Frequency Range: 26.965-27.405 MHz
- Channel Spacing: 10 kHz
- Total Channels: 40
- Authorized Modes: AM, SSB (USB/LSB)
- Power Limits: 4W AM, 12W PEP SSB
- Bandwidth: 10 kHz occupied

**DSB Modulation:**
- Double Sideband
- Similar to AM but can have reduced/suppressed carrier
- Bandwidth: ~10 kHz (for voice)
- Efficiency: Better than AM, worse than SSB

### 15.3 Radio Programming

**TK11 Programming Software:**
- File format: Binary (.dat)
- Record size: 64 bytes
- Capacity: 13,760 channels
- Encoding: Little-endian

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-29 | 1.0 | Initial plan created |
| TBD | 1.1 | Updated with test results and confirmed DSB mode value |

---

**END OF PLAN**

For questions or issues, review troubleshooting section or analyze with provided Python scripts.

**Good luck and transmit safely!**
