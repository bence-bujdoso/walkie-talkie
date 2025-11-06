# TK11 Patching Kit - Complete Package

This folder contains everything you need to patch the TK11 radio firmware and programming software to enable USB TX mode.

## 📁 Folder Structure

```
bin/
├── README.md                    # This file
├── original/                    # Place original files here
│   ├── TK11.exe                # Download from https://itistesla.com/ai/TK11.exe
│   └── TK11_v5.00.09_ENG.bin   # Download from https://itistesla.com/ai/TK11_v5.00.09_ENG.bin
├── patched_firmware/           # Generated patched firmware files (8 variants)
├── patched_software/           # Patched TK11.exe goes here
└── scripts/                    # Automation scripts
    ├── generate_patched_firmware.py        # Python script to generate firmware
    ├── patch_tk11_updata_method.cs         # dnSpy instructions (Level 1-2)
    ├── patch_tk11_downloadfileex_method.cs # dnSpy instructions (Level 3)
    ├── create_all_patches.sh              # Master script (Linux/Mac)
    └── create_all_patches.ps1             # Master script (Windows)
```

## 🚀 Quick Start

### Step 1: Download Original Files

1. **Download TK11.exe:**
   - URL: https://itistesla.com/ai/TK11.exe
   - Place in: `bin/original/`

2. **Download TK11 Firmware:**
   - URL: https://itistesla.com/ai/TK11_v5.00.09_ENG.bin
   - Place in: `bin/original/`

### Step 2: Generate Patched Firmware

**On Windows (PowerShell):**
```powershell
cd bin\scripts
.\create_all_patches.ps1
```

**On Linux/Mac (Bash):**
```bash
cd bin/scripts
chmod +x create_all_patches.sh
./create_all_patches.sh
```

**Or run Python script directly:**
```bash
cd bin/scripts
python3 generate_patched_firmware.py
```

This will create 8 patched firmware variants in `bin/patched_firmware/`.

### Step 3: Patch TK11.exe (Manual Step)

TK11.exe must be patched using **dnSpy** (Windows .NET decompiler):

1. **Download dnSpy:**
   - URL: https://github.com/dnSpyEx/dnSpy/releases
   - Extract and run `dnSpy.exe`

2. **Open TK11.exe:**
   - File → Open
   - Select: `bin/original/TK11.exe`

3. **Edit the Updata() method:**
   - In the left tree, navigate to: `K7` → `wfm_progress` → `Updata()`
   - Right-click on `Updata()` → **"Edit Method (C#)..."**
   - **DELETE ALL CODE** in the method
   - **COPY** the code from: `bin/scripts/patch_tk11_updata_method.cs`
   - **PASTE** into the editor
   - Click **"Compile"**

4. **Save patched TK11.exe:**
   - File → **Save Module**
   - Save as: `bin/patched_software/TK11_PATCHED.exe`

**Detailed instructions:** See `scripts/patch_tk11_updata_method.cs`

### Step 4: Test the Patched Firmware

1. **Start the patched TK11.exe:**
   ```
   bin/patched_software/TK11_PATCHED.exe
   ```

2. **Load patched firmware:**
   - Click "Update" or "Firmware Update"
   - Browse to: `bin/patched_firmware/TK11_PATCHED_v3_minimal.bin`
   - Click "Open"
   - **Expected:** No "File version is Wrong" error ✅

3. **Flash to radio:**
   - Connect radio in bootloader mode
   - Click "Update" or "Flash"
   - Wait for completion

4. **Test USB TX mode:**
   - Switch radio to USB mode (Mode 0x04)
   - Try to transmit
   - Should work without "DISABLE" message ✅

## 📦 What You Get

### Patched Firmware Variants (8 files)

All variants have USB TX enabled (byte at 0x314D changed from 0x03 to 0x13):

1. **TK11_PATCHED_v3_minimal.bin** ⭐ **START HERE**
   - Most conservative approach
   - Only 1 byte changed
   - Preserves all original structure
   - **Test this first!**

2. **TK11_PATCHED_v1_simple_crc16xmodem.bin**
   - CRC16-XMODEM calculated and placed at end of file
   - Good second choice if v3 fails

3. **TK11_PATCHED_v2_crc16ibm.bin**
   - CRC16-IBM algorithm
   - Alternative CRC approach

4. **TK11_PATCHED_v4_header_0x0C.bin**
   - CRC16-XMODEM at offset 0x0C (potential header position)

5. **TK11_PATCHED_v4_header_0x10.bin**
   - CRC16-XMODEM at offset 0x10

6. **TK11_PATCHED_v4_header_0x1C.bin**
   - CRC16-XMODEM at offset 0x1C

7. **TK11_PATCHED_v4_header_0x20.bin**
   - CRC16-XMODEM at offset 0x20

8. **TK11_PATCHED_v4_end_of_file.bin**
   - CRC16-XMODEM at end of file (same as v1)

### Patched Software

**TK11_PATCHED.exe** (you create this with dnSpy):
- Bypasses firmware validation
- Loads patched firmware directly
- Three-level bypass approach:
  - Level 1: Try original validation (for standard firmware)
  - Level 2: If fails, load file directly (for patched firmware)
  - Level 3: (Optional) Bypass bootloader checks too

## 🔧 Troubleshooting

### "File version is Wrong" Error

**Cause:** Using original TK11.exe, not patched version

**Fix:**
```bash
# Make sure you're using the patched version
# Windows:
copy bin\patched_software\TK11_PATCHED.exe TK11.exe

# Linux:
cp bin/patched_software/TK11_PATCHED.exe TK11.exe
```

### "Write fail" Error

**Cause:** Bootloader rejecting firmware format

**Fix:**
1. Try all 8 firmware variants in order (start with v3_minimal)
2. If all fail: Use **Level 3 bypass**
   - See: `scripts/patch_tk11_downloadfileex_method.cs`
   - Patches the bootloader handshake check

### Python Script Fails

**Cause:** Missing original firmware file

**Fix:**
```bash
# Make sure firmware is in the right place:
ls -la bin/original/TK11*.bin

# If missing, download it:
# https://itistesla.com/ai/TK11_v5.00.09_ENG.bin
```

### dnSpy Compilation Fails

**Cause:** Syntax error in pasted code

**Fix:**
- Copy the code from `patch_tk11_updata_method.cs` exactly
- Check all braces `{}` are matched
- Check all semicolons `;` are present
- Try again

## 📚 Additional Resources

- **TK11_BYPASS_QUICK_GUIDE.md** - Step-by-step dnSpy patching guide
- **SOLUTION_FILE_VERSION_WRONG.md** - Technical explanation of the problem
- **COMPLETE_TK11_BYPASS.md** - All bypass levels explained
- **TK11_FIRMWARE_FORMAT_DETAILED_ANALYSIS.md** - Deep dive into firmware format

## 🎯 Success Checklist

- [ ] Original files downloaded and placed in `bin/original/`
- [ ] Patched firmware variants generated (8 files in `bin/patched_firmware/`)
- [ ] TK11.exe patched with dnSpy (saved as `TK11_PATCHED.exe`)
- [ ] Patched firmware loads without "File version is Wrong" error
- [ ] Flash process completes successfully
- [ ] Radio boots normally
- [ ] USB TX mode works (no "DISABLE" message)

## ⚠️ Important Notes

### Backup Original Firmware

Before flashing, make sure you can restore the original firmware if needed:
- Keep the original `TK11_v5.00.09_ENG.bin` safe
- Test that the original firmware still works before trying patched versions
- If something goes wrong, flash the original firmware back

### Copyright Notice

- TK11.exe and firmware files are property of Quansheng Electronics
- This patching kit is for personal, educational use only
- Modifications void your warranty
- Use at your own risk

### Legal Compliance

**Radio Transmission Laws:**
- Check your local regulations before transmitting
- USB mode may not be legal for radio transmission in your region
- This patch enables TX for all modes - use responsibly
- You are responsible for compliance with radio regulations

## 🆘 Getting Help

If you encounter problems:

1. **Read the troubleshooting section above**
2. **Check the additional documentation:**
   - `TK11_BYPASS_QUICK_GUIDE.md`
   - `SOLUTION_FILE_VERSION_WRONG.md`
3. **Verify you followed all steps correctly**
4. **Test with the original firmware** (to verify radio/cable works)

## 🎉 Expected Results

After successful patching and flashing:

✅ TK11_PATCHED.exe loads patched firmware without errors
✅ Flash process completes to 100%
✅ Radio restarts automatically
✅ Radio functions normally (RX/TX on all modes)
✅ USB mode (0x04) allows transmission
✅ No "DISABLE" message in USB mode
✅ All other modes work as before

**Congratulations! Your TK11 radio now supports USB TX mode!**

---

**Good luck! 73! 📻**

**Version:** 1.0
**Date:** 2025-11-06
**Status:** Ready to use
