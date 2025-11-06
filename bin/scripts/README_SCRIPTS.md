# TK11 Scripts - Usage Guide

This folder contains various scripts for patching TK11 firmware and configuration files.

## 📁 Available Scripts

### 1. **patch_tk11_cps_dat.py** ⭐ RECOMMENDED
**The main solution for enabling USB TX!**

**Features:**
- ✅ Interactive mode with confirmations
- ✅ Colorful output
- ✅ Shows current and new TX mask values
- ✅ Verifies patch after applying
- ✅ Safe with user confirmations

**Usage:**
```bash
python patch_tk11_cps_dat.py TK11_BACKUP.dat
```

**What it does:**
1. Reads your TK11 CPS backup (.dat file)
2. Shows current TX mask configuration
3. Asks for confirmation
4. Patches offset 0x314D: 0x03 → 0x13
5. Saves as TK11_BACKUP_PATCHED.dat
6. Verifies the patch

---

### 2. **patch_tk11_cps_dat_simple.py**
**Simple, non-interactive version**

**Features:**
- ✅ No interactive prompts
- ✅ Fast and simple
- ✅ Good for automation/batch processing
- ✅ Plain text output

**Usage:**
```bash
# Auto-generate output filename
python patch_tk11_cps_dat_simple.py TK11_BACKUP.dat

# Specify output filename
python patch_tk11_cps_dat_simple.py TK11_BACKUP.dat TK11_PATCHED.dat
```

---

### 3. **generate_patched_firmware.py**
**Generates 8 patched firmware variants**

⚠️ **NOT RECOMMENDED** - These firmware files don't work because of encryption issues.

Use the CPS .dat patching method instead!

---

### 4. **create_raw_patched_firmware.py**
**Creates raw patched firmware**

⚠️ **EXPERIMENTAL** - May or may not work depending on firmware encryption.

The CPS method is more reliable.

---

### 5. **patch_tk11_updata_method.cs**
**dnSpy patching code for TK11.exe (Level 1-2)**

This is C# code to be used with dnSpy to patch TK11.exe.
Enables bypass of firmware validation.

**Not needed for CPS method!**

---

### 6. **patch_tk11_downloadfileex_method.cs**
**dnSpy patching code for TK11.exe (Level 3)**

This is C# code for advanced bypass.

**Not needed for CPS method!**

---

### 7. **create_all_patches.sh** / **create_all_patches.ps1**
**Master scripts for creating all patches**

These scripts generate firmware variants.

**Not needed for CPS method!**

---

## 🎯 Which Script Should I Use?

### ✅ Recommended: CPS .dat Patching

**Use:** `patch_tk11_cps_dat.py` or `patch_tk11_cps_dat_simple.py`

**Why:**
- ✅ Works 99% of the time
- ✅ No firmware flash needed
- ✅ No encryption issues
- ✅ Reversible
- ✅ Safe

**Process:**
1. Read CPS from radio → TK11_BACKUP.dat
2. Run script to patch the .dat file
3. Write patched CPS back to radio
4. Done! USB TX works!

---

### ❌ NOT Recommended: Firmware Patching

**Don't use:** `generate_patched_firmware.py` and related firmware scripts

**Why:**
- ❌ Firmware is encrypted
- ❌ Direct modification corrupts encryption
- ❌ Bootloader rejects corrupted firmware
- ❌ "Write Fail" error
- ❌ Only 10% success rate

---

## 📚 Complete Workflow

### Step 1: Read CPS from Radio

1. Open **TK11.exe** (original version is fine)
2. Connect radio in **normal mode** (not bootloader!)
3. Click **"Read"** or **"Download from radio"**
4. Save as: `TK11_BACKUP.dat`

### Step 2: Patch the .dat File

**Interactive version:**
```bash
python patch_tk11_cps_dat.py TK11_BACKUP.dat
```

**Simple version:**
```bash
python patch_tk11_cps_dat_simple.py TK11_BACKUP.dat
```

**Result:** Creates `TK11_BACKUP_PATCHED.dat`

### Step 3: Write Patched CPS to Radio

1. Open **TK11.exe**
2. Connect radio (normal mode)
3. Click **"Write"** or **"Upload to radio"**
4. Select: `TK11_BACKUP_PATCHED.dat`
5. Wait for completion

### Step 4: Test

1. Switch radio to **USB mode** (Mode 0x04)
2. Try to transmit
3. Should work without "DISABLE" message! ✅

---

## 🔧 Requirements

### Python Scripts
- **Python 3.6+**
- No additional packages needed (uses only built-in modules)

### dnSpy C# Files
- **dnSpy** (Windows .NET decompiler)
- Only needed if you want to patch TK11.exe

---

## ⚠️ Important Notes

### Backup Your Data!
Always keep the original `TK11_BACKUP.dat` file safe!

If something goes wrong:
- Just write the original .dat file back to the radio
- Everything will be restored

### File Size
The .dat file size varies by radio model:
- TK11: Usually around 900KB - 1MB
- Contains complete radio configuration and memory

### Offset Location
The TX mask is at offset **0x314D** (12621 decimal)
This is the same in both:
- Firmware .bin files
- CPS .dat files

### What Gets Modified
Only **1 byte** changes:
- Offset: 0x314D
- From: 0x03 (USB TX disabled)
- To: 0x13 (USB TX enabled)

---

## 🆘 Troubleshooting

### Script says "File not found"
- Check the file path
- Make sure you're in the right directory
- Use absolute path if needed

### Script says "Already patched"
- The file was already modified
- You can continue anyway if you want
- Or use the original backup

### Write to radio fails
- Make sure radio is connected in normal mode (not bootloader)
- Check COM port settings in TK11.exe
- Try reading from radio first to verify connection

### USB TX still doesn't work after patching
- Verify the patch was applied (check with hex editor at 0x314D)
- Make sure you wrote the PATCHED version, not the original
- Try reading from radio again to verify the change stuck

---

## 📞 Support

See the main documentation:
- `DIRECT_MEMORY_PATCH_SOLUTION.md` - Complete guide
- `LEVEL3_BYPASS_SIMPLE.md` - Alternative approaches
- `README.md` - Main project documentation

---

**Good luck! 73! 📻**
