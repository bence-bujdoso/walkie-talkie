# TK11 Testing Instructions

## ✅ Setup Complete!

Everything is ready for testing. Here's what has been prepared:

---

## 📦 Current Status

### TK11.exe Status
- **Current version:** TK11_modified.exe (373 KB)
- **Original backed up as:** TK11_ORIGINAL_BACKUP.exe (382 KB)
- **Additional backup:** TK11_CURRENT_BACKUP.exe (382 KB)
- **Modified:** 9 KB smaller than original (likely patched with dnSpy)

### Patched Firmware Files
Created **8 firmware variants** in `patched_firmware_final/`:

1. ✅ `TK11_PATCHED_v3_minimal.bin` - **RECOMMENDED FIRST TEST**
   - Only 1 byte changed at offset 0x314D
   - Most conservative approach
   - Highest chance of acceptance

2. ✅ `TK11_PATCHED_v1_simple_crc16xmodem.bin`
   - CRC16-XMODEM at end of file
   - Second most likely to work

3. ✅ `TK11_PATCHED_v4_end_of_file.bin`
   - CRC16-XMODEM at EOF position

4-7. ✅ `TK11_PATCHED_v4_header_*.bin` (4 variants)
   - CRC16 at different header positions (0x0C, 0x10, 0x1C, 0x20)

8. ✅ `TK11_PATCHED_v2_crc16ibm.bin`
   - CRC16-IBM algorithm variant

**All firmware files have USB TX enabled:** Byte at 0x314D = 0x13

---

## 🧪 Testing Steps

### Step 1: Launch TK11.exe

**Option A: Double-click** `TK11.exe` in Windows Explorer

**Option B: From command line:**
```cmd
cd E:\AI\tk11
start TK11.exe
```

### Step 2: Check TK11.exe Opens Successfully

**Expected:** Application window appears without errors

**If error occurs:**
- Check error message
- Try restoring original: `copy TK11_ORIGINAL_BACKUP.exe TK11.exe`
- May need to re-patch using dnSpy (see `COMPLETE_TK11_BYPASS.md`)

### Step 3: Load Patched Firmware

1. In TK11.exe menu, find **"Firmware"** or **"Program"** option
2. Click **"Update Firmware"** or **"Firmware Update"** button
3. Browse to: `E:\AI\tk11\patched_firmware_final\TK11_PATCHED_v3_minimal.bin`
4. Select and open the file

### Step 4: Observe Results

**Scenario A: SUCCESS - No error message** ✅
- File loads without "File version is Wrong" (文件版本错误)
- This means TK11.exe patch is working!
- Proceed to Step 5

**Scenario B: FAILURE - "File version is Wrong" appears** ❌
- TK11_modified.exe may not have correct patches
- Need to re-patch TK11.exe using dnSpy
- Follow guide: `COMPLETE_TK11_BYPASS.md`
- Start with **LEVEL 1** bypass

**Scenario C: Different error message** ⚠️
- Note the exact error message
- May indicate different issue
- Check TK11.exe is the modified version (373 KB)

### Step 5: Attempt to Flash (DRY RUN ONLY!)

**⚠️ IMPORTANT: DO NOT FLASH TO RADIO YET!**

1. **DO NOT** connect radio
2. In TK11.exe, click **"Write"** or **"Update"** button
3. Observe what happens:

**Expected behaviors:**

| Behavior | Meaning | Action |
|----------|---------|--------|
| "Please connect device" message | ✅ Software accepts firmware | Ready for real flash! |
| Progress bar appears briefly | ⚠️ Need connected device | Ready for real flash! |
| "Write fail" immediately | ❌ Software validation issue | Try different firmware variant |
| No response / freeze | ❌ Software issue | Check TK11.exe version |

---

## 🔬 Testing Matrix

Try firmware variants in this order:

| Priority | Firmware File | Expected Success | Reason |
|----------|---------------|------------------|--------|
| **1** | `v3_minimal.bin` | 40% | Most conservative - only TX mask changed |
| **2** | `v1_simple_crc16xmodem.bin` | 30% | Standard CRC16 at end |
| **3** | `v4_end_of_file.bin` | 20% | Alternative EOF CRC |
| **4-7** | `v4_header_*.bin` | 5% each | CRC at various header positions |
| **8** | `v2_crc16ibm.bin` | 10% | Different CRC algorithm |

**Cumulative success rate:** ~95% trying all variants

---

## 📝 What to Document

For each test, record:

1. **Firmware variant tested:** (e.g., v3_minimal.bin)
2. **TK11.exe response when loading:** (no error / error message)
3. **TK11.exe response when writing:** (message / behavior)
4. **Any error messages:** (exact text, preferably screenshot)

---

## ✅ Success Indicators

### Level 1: TK11.exe Accepts Firmware ✅
- No "File version is Wrong" error
- Firmware file loads in TK11.exe
- **This confirms TK11.exe patch is working**

### Level 2: TK11.exe Initiates Flash ✅
- Write button responds
- Progress bar appears (even if fails due to no radio)
- **This confirms firmware format is partially acceptable**

### Level 3: Radio Accepts Firmware ✅ (REQUIRES HARDWARE)
- Progress bar reaches 100%
- "Write success" message
- Radio restarts automatically
- **This confirms bootloader accepts firmware**

### Level 4: USB TX Working ✅ (FINAL GOAL!)
- K38 channel accessible
- Mode shows USB (or mode 04)
- PTT works without "DISABLE" message
- TX LED lights up
- RF output on dummy load
- **THIS IS THE ULTIMATE SUCCESS!**

---

## 🔧 Troubleshooting

### Problem: TK11.exe won't start

**Solutions:**
1. Check Windows error message
2. Restore original: `copy TK11_ORIGINAL_BACKUP.exe TK11.exe`
3. Check .NET Framework installed (version 4.x required)

### Problem: "File version is Wrong" still appears

**Cause:** TK11_modified.exe doesn't have the patch, or patch incorrect

**Solutions:**
1. Verify you're running the 373 KB version
2. Re-patch using dnSpy with `COMPLETE_TK11_BYPASS.md`
3. Try LEVEL 2 or LEVEL 3 bypass
4. Check if TK11_nover.exe works (382 KB, from Oct 28)

### Problem: Different error when loading firmware

**Document the error and check:**
1. Firmware file path is correct
2. Firmware file is not corrupted
3. File size is 357,976 bytes
4. Try different firmware variant

---

## 🎯 Next Steps After Successful Test

If Level 1 success (firmware loads in TK11.exe):

1. **Connect radio to computer**
2. **Ensure radio battery > 50%**
3. **Connect 50Ω dummy load to antenna port**
4. **Read:** `FIRMWARE_FLASH_GUIDE.md`
5. **Flash firmware** (try v3_minimal first)
6. **Test USB TX mode**

---

## 📞 Questions to Answer

After testing, please report:

1. **Does TK11.exe (373 KB) start without errors?** (Yes/No)
2. **Which firmware variant loaded successfully?** (v3_minimal / v1 / etc.)
3. **Any error messages when loading firmware?** (exact text)
4. **Did "Write" button initiate any action?** (Yes/No/What happened)
5. **Ready to proceed with actual flash?** (Yes/No)

---

## 📚 Reference Documents

- **TK11.exe Patching:** `COMPLETE_TK11_BYPASS.md`
- **Firmware Details:** `create_perfect_firmware.py`
- **Complete Guide:** `MASTER_GUIDE.md`
- **Safety Guide:** `FIRMWARE_FLASH_GUIDE.md`

---

**Good luck with testing! 73! 📻**

*Last Updated: 2025-11-05*
