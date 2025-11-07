# TK11 Patching - Quick Start (5 Minutes)

## 📥 Step 1: Download Files (2 minutes)

Download these two files and place them in `bin/original/`:

1. **TK11.exe**: https://itistesla.com/ai/TK11.exe
2. **Firmware**: https://itistesla.com/ai/TK11_v5.00.09_ENG.bin

```
bin/original/
├── TK11.exe
└── TK11_v5.00.09_ENG.bin
```

## 🔧 Step 2: Generate Patched Firmware (1 minute)

**Windows (PowerShell):**
```powershell
cd bin\scripts
.\create_all_patches.ps1
```

**Linux/Mac:**
```bash
cd bin/scripts
./create_all_patches.sh
```

**Result:** 8 patched firmware files created in `bin/patched_firmware/`

## 🛠️ Step 3: Patch TK11.exe (2 minutes)

1. **Open dnSpy:** Download from https://github.com/dnSpyEx/dnSpy/releases
2. **Load:** `bin/original/TK11.exe`
3. **Navigate:** `K7` → `wfm_progress` → `Updata()`
4. **Right-click:** `Updata()` → "Edit Method (C#)..."
5. **Replace code:** Copy from `bin/scripts/patch_tk11_updata_method.cs`
6. **Compile:** Click "Compile" button
7. **Save:** File → Save Module → `bin/patched_software/TK11_PATCHED.exe`

## 🚀 Step 4: Flash to Radio

1. **Run:** `bin/patched_software/TK11_PATCHED.exe`
2. **Load firmware:** Browse to `bin/patched_firmware/TK11_PATCHED_v3_minimal.bin`
3. **Flash:** Connect radio, click "Update"
4. **Done!** ✅

## ✅ Success!

Your TK11 now supports USB TX mode! No more "DISABLE" message.

---

**Full documentation:** See `bin/README.md`

**73! 📻**
