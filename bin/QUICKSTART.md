# TK11 USB TX Unlock - Quick Start Guide

**Total time: 15-30 minutes** | **Difficulty: Medium** | **Risk: Low (with backup)**

---

## 📋 Prerequisites

- Windows PC
- TK11 radio with USB cable
- 50Ω dummy load (REQUIRED for safety!)
- Python 3.x installed
- dnSpy (included in repository)

---

## 🚀 5-Step Process

### Step 1: Download Original Files (2 minutes)

Download these two files and place them in `bin/original/`:

```
https://itistesla.com/ai/TK11_v5.00.09_ENG.bin
https://itistesla.com/ai/TK11.exe
```

**Verify:**
```
bin/original/
├── TK11.exe
└── TK11_v5.00.09_ENG.bin
```

---

### Step 2: Generate Patched Firmware (1 minute)

**Windows:**
```powershell
cd bin\scripts
.\create_all_patches.ps1
```

**Linux/Mac:**
```bash
cd bin/scripts
./create_all_patches.sh
```

**Result:** 8 firmware variants created in `patched_firmware_final/`

---

### Step 3: Patch TK11.exe (5 minutes)

1. **Backup original:**
   ```cmd
   copy bin\original\TK11.exe bin\original\TK11_ORIGINAL_BACKUP.exe
   ```

2. **Open dnSpy:**
   ```cmd
   dnSpy\dnSpy.exe bin\original\TK11.exe
   ```

3. **Navigate to:**
   ```
   TK11 → K7 → wfm_progress → Updata()
   ```

4. **Edit method:**
   - Right-click `Updata()` → "Edit Method (C#)..."
   - Copy entire code from: `bin\scripts\patch_tk11_updata_method.cs`
   - Paste and replace
   - Click "Compile"

5. **Save:**
   - File → Save Module
   - Save as: `TK11_PATCHED.exe`

**Verification:**
- File size should be ~373 KB (original is ~382 KB)
- Open TK11_PATCHED.exe - should start normally

---

### Step 4: Flash Firmware to Radio (5-10 minutes)

1. **Connect radio:**
   - Turn OFF radio
   - Connect USB cable
   - Turn ON radio

2. **Open TK11_PATCHED.exe**

3. **Load firmware:**
   - Click "Open" or firmware browse button
   - Select: `patched_firmware_final\TK11_PATCHED_v3_minimal.bin`
   - Should see: "Firmware loaded (validation bypassed)" ✅

4. **Flash:**
   - Click "Write" or "Update"
   - Watch progress bar
   - Wait for completion

**Expected results:**
- ✅ "Write success" → **SUCCESS! Go to Step 5**
- ❌ "Write fail" → Try next variant (v1, v2, v4)

**Firmware testing order:**
1. `TK11_PATCHED_v3_minimal.bin` (most conservative)
2. `TK11_PATCHED_v1_simple_crc16xmodem.bin`
3. `TK11_PATCHED_v4_end_of_file.bin`
4. Other v4_header_* variants
5. `TK11_PATCHED_v2_crc16ibm.bin`

---

### Step 5: Test USB TX (5 minutes)

1. **Wait for radio restart** (automatic after flash)

2. **Connect dummy load** (50Ω) to antenna port ⚠️

3. **Navigate to K38 channel:**
   - Frequency: 27.385 MHz
   - Should be in channel list

4. **Select USB mode:**
   - Menu → Modulation → USB
   - Or cycle through modes

5. **Test transmission:**
   - Press PTT button
   - **Expected:** NO "DISABLE" message ✅
   - TX LED should light up
   - Should transmit normally

6. **SUCCESS!** 🎉

---

## ⚠️ Safety Warnings

- ⚠️ **ALWAYS use 50Ω dummy load for testing TX**
- ⚠️ **Backup original firmware before flashing**
- ⚠️ **Risk of radio brick if done incorrectly**
- ⚠️ **USB mode may not produce true SSB signal (BK4819 limitation)**
- ⚠️ **Legal:** Use only for authorized testing with proper license

---

## 🔧 Troubleshooting

### "Python not found"
**Fix:** Install Python from https://www.python.org/

### "File version is Wrong" error in TK11.exe
**Cause:** Using original TK11.exe instead of patched
**Fix:** Make sure you're using TK11_PATCHED.exe

### "Write fail" with all firmware variants
**Cause:** Bootloader very strict
**Fix:**
- Check USB cable connection
- Try turning radio OFF then ON
- See `bin\README.md` for advanced troubleshooting
- Consider LEVEL 3 bypass (see COMPLETE_TK11_BYPASS.md)

### "Compilation failed" in dnSpy
**Cause:** Syntax error in pasted code
**Fix:**
- Copy code from `patch_tk11_updata_method.cs` again carefully
- Check all `{ }` braces match
- Check all `;` semicolons present
- Try LEVEL 1 bypass (alternative code in the file)

### Radio won't start after flash
**Cause:** Bad firmware flash
**Fix:**
- Reconnect USB cable
- Flash original firmware: `TK11_v5.00.09_ENG.bin`
- Use original TK11.exe (from bin/original/TK11_ORIGINAL_BACKUP.exe)

---

## 📚 More Help

- **Detailed guide:** `bin\README.md`
- **dnSpy instructions:** `COMPLETE_TK11_BYPASS.md`
- **Technical details:** `TX_UNLOCK_REPORT.md`
- **Firmware analysis:** `TK11_FIRMWARE_FORMAT_DETAILED_ANALYSIS.md`

---

## ✅ Success Checklist

- [ ] Downloaded original files to bin/original/
- [ ] Generated 8 firmware variants
- [ ] Patched TK11.exe with dnSpy
- [ ] Flashed firmware successfully ("Write success")
- [ ] Radio restarted and works normally
- [ ] K38 channel accessible
- [ ] USB mode selectable
- [ ] PTT works without "DISABLE" message
- [ ] **MISSION COMPLETE!** 🎉

---

**Good luck! 73! 📻**