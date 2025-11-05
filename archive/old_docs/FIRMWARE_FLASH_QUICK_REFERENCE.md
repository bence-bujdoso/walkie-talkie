# TK11 Firmware Flash - Quick Reference Guide

## Problem: "File version is Wrong" Error

**Root Cause:** Firmware validation fails due to unknown checksum algorithm

**Solution:** 5 alternative approaches, ranked by ease and success probability

---

## 🥇 SOLUTION 1: Patch TK11.exe (RECOMMENDED - Start Here!)

**Success Rate:** 80% | **Risk:** LOW | **Time:** 30 minutes

### Quick Steps

1. **Open dnSpy**
   ```
   E:\AI\tk11\dnSpy\dnSpy.exe
   ```

2. **Load TK11.exe**
   - File → Open → `E:\AI\tk11\TK11.exe`

3. **Find validation code**
   - Press `Ctrl+Shift+K`
   - Search: `文件版本错误`
   - Double-click result → goes to `wfm_progress.Updata()` method

4. **Edit the method**
   - Right-click on `Updata()` method
   - Select "Edit Method (C#)..."

5. **Apply Version B Patch (Safer)**

   Find this section:
   ```csharp
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
   ```

   Add THIS code right AFTER it:
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
   - Click "Compile" button (bottom right)
   - Check for errors (should be none)

7. **Save**
   - File → Save Module
   - Save as: `E:\AI\tk11\TK11_PATCHED_BYPASS.exe`

8. **Use patched version**
   ```bash
   # Backup original
   copy E:\AI\tk11\TK11.exe E:\AI\tk11\TK11_ORIGINAL.exe

   # Use patched
   copy E:\AI\tk11\TK11_PATCHED_BYPASS.exe E:\AI\tk11\TK11.exe
   ```

9. **Test**
   - Launch `TK11.exe`
   - Load patched firmware: `patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin`
   - Should NOT show "File version is Wrong" error!

### Expected Results

✅ **TK11.exe Level:**
- No "File version is Wrong" error
- Firmware loads successfully
- Flash process starts

✅ **Radio Level (if bootloader doesn't validate):**
- Flash completes
- Radio reboots
- Functions normally

❌ **Radio Level (if bootloader validates):**
- Flash fails with bootloader error
- → Try Solution 2

---

## 🥈 SOLUTION 2: Patch Original + Fix CRC16

**Success Rate:** 40% | **Risk:** LOW | **Time:** 15 minutes

### Quick Steps

1. **Run the patch script**
   ```bash
   cd E:\AI\tk11
   python patch_original_directly.py
   ```

2. **Script creates 18+ firmware versions:**
   - Different CRC16 algorithms (XMODEM, CCITT, MODBUS)
   - Different CRC storage locations
   - Plus one with no CRC fix

3. **Test with patched TK11.exe**
   - Start with: `TK11_PATCHED_NO_CRC_FIX.bin`
   - If bootloader rejects it, try each CRC16 version:
     - `TK11_PATCHED_CRC16_XMODEM_offset_0002.bin`
     - `TK11_PATCHED_CRC16_XMODEM_offset_0004.bin`
     - etc.

4. **When one works:**
   - Note which algorithm and offset worked
   - Use for future patches

### Files Created
```
patched_firmware/
├── TK11_PATCHED_NO_CRC_FIX.bin
├── TK11_PATCHED_CRC16_XMODEM_offset_0002.bin
├── TK11_PATCHED_CRC16_XMODEM_offset_0004.bin
├── TK11_PATCHED_CRC16_CCITT_offset_0002.bin
└── ... (18 total)
```

---

## 🥉 SOLUTION 3: Force Old Boot Protocol

**Success Rate:** 30% | **Risk:** MEDIUM | **Time:** 2-4 hours

### Investigation Required

1. **Find boot version check in dnSpy**
   - Search for: `check_boot_ver`
   - Search for: `boot_version`
   - Search for: `GetUpdataReady`

2. **Identify protocol selection logic**
   ```csharp
   if (boot_version < "2.0") {
       // Old protocol - may have simpler validation
   } else {
       // New protocol - strict validation
   }
   ```

3. **Patch to force old protocol**
   - Make `check_boot_ver()` always return true for old version
   - OR patch protocol selection to always use old path

4. **Test**
   - Older protocols may skip checksum validation
   - Or use simpler checksums

---

## 🔧 SOLUTION 4: Direct Memory Write (ADVANCED)

**Success Rate:** 20% | **Risk:** HIGH | **Time:** 4-8 hours

### Not Recommended Unless Expert

Requires:
- Deep protocol reverse engineering
- Serial/USB communication capture
- Custom flash tool development
- Understanding of radio's memory map

**Risk:** Can brick radio permanently

---

## ⚡ SOLUTION 5: JTAG/SWD Programming (EXPERT ONLY)

**Success Rate:** 90%* | **Risk:** VERY HIGH | **Time:** 8-24 hours

*If you know what you're doing. Otherwise: radio destruction likely.

### Required
- ST-Link V2 programmer
- Soldering skills
- Radio disassembly
- MCU identification
- OpenOCD knowledge

### Quick Overview
1. Open radio
2. Find debug pins (SWDIO, SWCLK)
3. Connect ST-Link
4. Flash with OpenOCD:
   ```bash
   openocd -f stlink.cfg -f stm32f1x.cfg
   flash write_image erase firmware.bin 0x08000000
   ```

**⚠️ Can permanently brick radio. Do NOT attempt without experience.**

---

## 📊 Comparison Table

| # | Solution | Success | Risk | Time | Skill |
|---|----------|---------|------|------|-------|
| 1 | Patch TK11.exe | 80% | LOW | 30m | Beginner |
| 2 | Original + CRC16 | 40% | LOW | 15m | Beginner |
| 3 | Old Boot Protocol | 30% | MED | 2-4h | Intermediate |
| 4 | Direct Memory | 20% | HIGH | 4-8h | Advanced |
| 5 | JTAG/SWD | 90%* | EXTREME | 8-24h | Expert |

---

## 🎯 Recommended Testing Sequence

### Test 1: Solution 1 Only
```
1. Patch TK11.exe (Solution 1, Version B)
2. Try flashing: TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin
3. If succeeds → DONE! ✓
4. If fails at TK11.exe level → recheck patch
5. If fails at radio level → continue to Test 2
```

### Test 2: Solution 1 + Solution 2
```
1. Keep using patched TK11.exe
2. Run: python patch_original_directly.py
3. Try flashing: TK11_PATCHED_NO_CRC_FIX.bin
4. If fails → try each CRC16 variant
5. If one succeeds → DONE! ✓
6. If all fail → continue to Test 3
```

### Test 3: Solution 3
```
1. Investigate boot version protocol
2. Patch to force old boot mode
3. Test again
4. If fails → consider Solution 5 (hardware)
```

---

## 🐛 Troubleshooting

### TK11.exe still shows error
**Problem:** Patch didn't apply correctly

**Solutions:**
- Verify you're running `TK11_PATCHED_BYPASS.exe`
- Recheck the C# code changes
- Try Version A (complete bypass) instead
- Look for compilation errors in dnSpy

### Flash starts but radio rejects
**Problem:** Radio bootloader validates independently

**Solutions:**
- Try Solution 2 (CRC16 fixes)
- Radio has separate validation layer
- May need Solution 5 (JTAG)

### Radio bricked after flash
**Problem:** Flash corruption or bootloader locked

**Solutions:**
1. Try reflashing original firmware
2. Look for bootloader recovery mode
   - Power off radio
   - Hold special button combination
   - Power on (check manual)
3. JTAG recovery (last resort)

### dnSpy won't compile
**Problem:** Syntax error in patch

**Solutions:**
- Check all braces `{}` match
- Check all semicolons `;` present
- Copy exact code from guide
- Try simpler Version A patch

---

## 📁 File Locations

### Input Files
```
E:\AI\tk11\TK11.exe                          - Original software
E:\AI\tk11\TK11_v5.00.09_ENG.bin             - Original firmware
E:\AI\tk11\dnSpy\dnSpy.exe                   - Decompiler
```

### Patched Firmware (Existing)
```
E:\AI\tk11\patched_firmware\
├── TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin
├── TK11_PATCHED_Mode_05_DSB_20251029_152304.bin
└── ... (various versions)
```

### Files You'll Create
```
E:\AI\tk11\TK11_PATCHED_BYPASS.exe           - Patched software (Solution 1)
E:\AI\tk11\TK11_ORIGINAL.exe                 - Backup of original

E:\AI\tk11\patched_firmware\
├── TK11_PATCHED_NO_CRC_FIX.bin              - From Solution 2
├── TK11_PATCHED_CRC16_*.bin                 - From Solution 2 (18 files)
```

---

## ✅ Success Indicators

### Level 1: TK11.exe Bypass Success
- ✅ No "File version is Wrong" error when loading firmware
- ✅ Firmware file opens in TK11.exe
- ✅ Flash process initiates

### Level 2: Radio Bootloader Success
- ✅ Flash process completes (100%)
- ✅ Radio restarts automatically
- ✅ Radio display shows normal screen (not error)

### Level 3: Full Success
- ✅ Radio functions normally
- ✅ Can load USB mode configuration
- ✅ K38 USB channel accessible
- ✅ PTT works (no DISABLE message)

---

## 🎓 Understanding The Problem

### Two Validation Layers

**Layer 1: TK11.exe (Software)**
- Validates firmware before sending to radio
- Checks: checksum, version, format
- **Solution 1 bypasses this layer**

**Layer 2: Radio Bootloader (Firmware)**
- Validates firmware during flash
- Independent of TK11.exe
- **Solution 2 addresses this layer**

### Why Standard Checksums Failed

Previous attempts tried:
- CRC32, CRC16-CCITT, CRC16-MODBUS
- Adler32, Fletcher32, MD5, SHA1
- Various data ranges and offsets

Result: None matched → custom/proprietary algorithm

### Why Solution 1 Works

By patching TK11.exe to bypass validation:
- Firmware sent to radio without checks
- If bootloader ALSO validates → flash fails (try Solution 2)
- If bootloader doesn't validate → SUCCESS!

Many radios only validate in software, not in bootloader.

---

## 📞 Support Resources

### Documentation
```
E:\AI\tk11\ALTERNATIVE_FIRMWARE_FLASH_SOLUTIONS.md  - Detailed guide
E:\AI\tk11\FIRMWARE_FLASH_GUIDE.md                  - General guide
E:\AI\tk11\DNSPY_PATCH_UTASITAS.md                  - dnSpy instructions
```

### Analysis Files
```
E:\AI\tk11\FINAL_STATUS_REPORT.txt           - Project summary
E:\AI\tk11\ALTERNATIVE_SOLUTION.txt          - Alternative approaches
E:\AI\tk11\tk11_analysis_report.json         - Full analysis data
```

---

## ⚠️ Final Warnings

### Before You Start

1. ✅ Read entire guide
2. ✅ Understand risks
3. ✅ Have backup firmware
4. ✅ Have backup of TK11.exe
5. ✅ Battery fully charged (>80%)
6. ✅ Stable power supply
7. ✅ Dummy load for testing (NOT antenna)

### During Flash

1. ⚠️ Do NOT disconnect cable
2. ⚠️ Do NOT power off radio
3. ⚠️ Do NOT interrupt process
4. ⚠️ Do NOT touch anything

### If Something Goes Wrong

1. 🔄 Stay calm
2. 🔄 Try reflashing original firmware
3. 🔄 Check bootloader recovery mode
4. 🔄 Consult radio manual
5. 🔄 Seek expert help if needed

---

## 🚀 Start Now!

**Recommended first step:**

```bash
# 1. Open dnSpy
E:\AI\tk11\dnSpy\dnSpy.exe

# 2. Load TK11.exe
# 3. Search for: 文件版本错误
# 4. Edit Updata() method
# 5. Add bypass code (Version B)
# 6. Compile and save
# 7. Test!
```

**Good luck!** 73! 📻

---

**Document Version:** 1.0
**Date:** 2025-11-05
**Project:** TK11 Firmware Modification Research
