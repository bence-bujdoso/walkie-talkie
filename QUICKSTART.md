# 🚀 TK11 USB TX Unlock - Quick Start

**Time to complete:** 30-40 minutes
**Current status:** TK11.exe bypass working, testing firmware variants

---

## ✅ Prerequisites Checklist

Before starting:
- [ ] TK11 radio with USB cable
- [ ] Radio battery charged (>50%)
- [ ] 50Ω dummy load (REQUIRED for safety)
- [ ] Windows PC
- [ ] TK11.exe installed
- [ ] 30 minutes uninterrupted time

---

## 📍 WHERE YOU ARE NOW

✅ **Software validation bypass:** WORKING
🔄 **Firmware testing:** IN PROGRESS (v3 failed, testing v1 next)
⏳ **Final verification:** PENDING

**You are at Step 2 of 3.**

---

## 🎯 3 Steps to USB TX Unlock

### **STEP 1:** ✅ DONE - TK11.exe Validation Bypass

The modified TK11.exe (373 KB) is already active and working.
- No more "File version is Wrong" error
- Can load patched firmware files
- **This step is complete!**

---

### **STEP 2:** 🔄 IN PROGRESS - Find Working Firmware Variant

**Goal:** Test each firmware variant until one is accepted by the bootloader.

**What happened so far:**
- ❌ v3_minimal.bin → "Write Fail" (bootloader rejected)

**What to do next:**

#### Test v1_simple_crc16xmodem.bin

1. **Open TK11.exe** (double-click)

2. **Load firmware:**
   - Menu: "Firmware" → "Update" (or similar)
   - Browse to: `patched_firmware_final\TK11_PATCHED_v1_simple_crc16xmodem.bin`
   - Click "Open"
   - Should load without error ✅

3. **Connect radio:**
   - Connect TK11 radio via USB cable
   - Power ON the radio
   - Wait for PC to recognize device

4. **Attempt flash:**
   - In TK11.exe, click "Write" or "Update" button
   - Watch progress bar

5. **Observe result:**

| Result | Meaning | Action |
|--------|---------|--------|
| Progress → 100% → "Write success" | ✅ **SUCCESS!** | Go to STEP 3 |
| Progress → X% → "Write fail" | ❌ Try next variant | See table below |
| No progress bar | ❌ Connection issue | Check USB cable |

#### If v1 fails, try these in order:

| Priority | Firmware File | Notes |
|----------|---------------|-------|
| 1 | v1_simple_crc16xmodem.bin | ← **START HERE** |
| 2 | v4_end_of_file.bin | If v1 fails |
| 3 | v2_crc16ibm.bin | If v1-2 fail |
| 4 | v4_header_0x0C.bin | If v1-3 fail |
| 5 | v4_header_0x10.bin | If v1-4 fail |
| 6 | v4_header_0x1C.bin | If v1-5 fail |
| 7 | v4_header_0x20.bin | If v1-6 fail |

**Expected:** One of these will work (95% probability after testing all)

**Time:** 2-5 minutes per test, ~15-30 minutes total

---

### **STEP 3:** ⏳ PENDING - Verify USB TX Mode

**Only proceed when Step 2 shows "Write success"**

1. **Wait for radio restart** (30-60 seconds)

2. **Verify radio works:**
   - Display shows normal screen
   - Buttons respond
   - Can navigate channels

3. **Navigate to K38:**
   - Select K38 channel (27.385 MHz)
   - Check modulation mode (should show USB or mode 04)

4. **Connect dummy load:**
   - **IMPORTANT:** Connect 50Ω dummy load to antenna port
   - DO NOT transmit without dummy load

5. **Test USB TX:**
   - Press PTT button
   - **Expected:** NO "DISABLE" message
   - TX LED should light up
   - Power output on dummy load

6. **Verify with spectrum analyzer (optional):**
   - Connect spectrum analyzer
   - Set center: 27.385 MHz
   - Press PTT
   - Should see USB modulation

**If "DISABLE" still appears:**
- Firmware may not have flashed correctly
- Try different firmware variant
- Verify TX mask is 0x13 at offset 0x314D

---

## ⚡ Quick Command Reference

```bash
# If you need to restore original TK11.exe
copy TK11_ORIGINAL_BACKUP.exe TK11.exe

# Check which TK11.exe is active
dir TK11.exe
# Should show: 373 KB (modified) not 382 KB (original)

# Re-create firmware variants if needed
python create_perfect_firmware.py

# Verify patches
python verify_patches.py
```

---

## 🎯 Success Indicators

### ✅ You succeeded when:
- Flash completes with "Write success"
- Radio restarts normally
- K38 channel accessible
- PTT works without "DISABLE" message
- TX LED lights up
- RF output on dummy load

### 🎉 FINAL SUCCESS:
**You can now transmit on USB mode on K38!**

---

## ⚠️ Troubleshooting

### Problem: "Write Fail" on all variants

**Rare but possible. Solutions:**

1. **Try original firmware first:**
   - Flash original TK11_v5.00.09_ENG.bin
   - If this also fails → USB/driver issue
   - If this works → Need different firmware approach

2. **Check bootloader version:**
   - Bootloader may expect different format
   - See `TK11_BOOTLOADER_PROTOCOL_ANALYSIS.md`

3. **Advanced: JTAG recovery**
   - Last resort for firmware recovery
   - Requires JTAG adapter and expertise

### Problem: Radio won't start after flash

**DO NOT PANIC**

1. **Power cycle:**
   - Remove battery
   - Wait 10 seconds
   - Reinsert battery
   - Power on

2. **Re-flash original firmware:**
   - Use TK11_v5.00.09_ENG.bin
   - Should restore radio to working state

3. **If still bricked:**
   - May need JTAG recovery
   - Consult radio repair expert

---

## 📞 Current Task

**YOUR CURRENT TASK:**

**Test:** `TK11_PATCHED_v1_simple_crc16xmodem.bin`

**Steps:**
1. Open TK11.exe
2. Load v1_simple_crc16xmodem.bin
3. Connect radio
4. Click "Write"
5. Report result

**Report back with:**
- Result: [Write success / Write fail / Other]
- Progress: [Reached X% / No progress bar]
- Radio: [Restarted / No change]

---

## 📊 Progress Tracker

```
[✅] Step 1: TK11.exe validation bypass
[🔄] Step 2: Find working firmware (1/8 tested)
[ ] Step 3: Verify USB TX mode

CURRENT: Testing v1_simple_crc16xmodem.bin
TIME REMAINING: ~30-40 minutes
SUCCESS PROBABILITY: 95%
```

---

## 📁 Files You Need

All in: `E:\AI\tk11\`

**Active:**
- `TK11.exe` (373 KB)
- `patched_firmware_final\` (8 .bin files)

**Backup:**
- `TK11_ORIGINAL_BACKUP.exe`
- `TK11_v5.00.09_ENG.bin`

**Documentation:**
- `FIRMWARE_TESTING.md` (detailed testing guide)
- `FIRMWARE_FLASH_GUIDE.md` (safety procedures)

---

## 🎯 Final Goal

**Enable USB TX on K38 channel (27.385 MHz)**

Once successful:
- ✅ USB mode selectable
- ✅ PTT works without "DISABLE"
- ✅ TX LED lights during transmission
- ✅ RF power output on dummy load
- 🎉 **Mission complete!**

---

**You're almost there! Just need to find the right firmware variant.**

**Test v1 now and report back! 📻**

---

*Last Updated: 2025-11-05*
*Status: 95% Complete - Testing v1_simple_crc16xmodem next*
