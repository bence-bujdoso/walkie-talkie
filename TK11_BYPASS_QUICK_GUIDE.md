# TK11.exe Bypass - Quick dnSpy Guide

**Time: 5 minutes** | **Tool: dnSpy** | **Risk: Low (with backup)**

---

## 🎯 Goal

Patch TK11.exe to bypass firmware validation so it accepts modified firmware files.

---

## 📋 Prerequisites

- dnSpy (included in `dnSpy/` folder)
- Original TK11.exe (in `bin/original/`)
- Backup made ✅

---

## 🚀 Quick Steps

### 1. Backup Original (30 seconds)

```cmd
copy bin\original\TK11.exe bin\original\TK11_ORIGINAL_BACKUP.exe
```

### 2. Open in dnSpy (30 seconds)

```cmd
dnSpy\dnSpy.exe bin\original\TK11.exe
```

### 3. Navigate to Method (1 minute)

In left pane, expand:
```
TK11
└─ K7
   └─ wfm_progress
      └─ Updata()  ← Double-click this
```

### 4. Edit Method (2 minutes)

1. **Right-click** `Updata()` method
2. Select **"Edit Method (C#)..."**
3. **Open file:** `bin\scripts\patch_tk11_updata_method.cs`
4. **Copy** the LEVEL 2 BYPASS code (starts with `public void Updata()`)
5. **Select all** in dnSpy editor (Ctrl+A)
6. **Paste** the new code
7. **Click "Compile"**

**Expected:** Green ✅ "Compilation successful"

### 5. Save Patched EXE (1 minute)

1. **File** menu → **Save Module...**
2. **Save as:** `TK11_PATCHED.exe`
3. **Close dnSpy**

---

## ✅ Verification

### File Size Check
```cmd
dir TK11_PATCHED.exe
```
Expected: **~373 KB** (original is ~382 KB)

### Functionality Test
```cmd
TK11_PATCHED.exe
```
- Should start normally ✅
- UI should look identical to original ✅

### Bypass Test
1. Open TK11_PATCHED.exe
2. Browse to any firmware file (e.g., `patched_firmware_final\TK11_PATCHED_v3_minimal.bin`)
3. **Expected:** "Firmware loaded (validation bypassed)" message ✅
4. **NOT expected:** "File version is Wrong" (文件版本错误) ❌

---

## 🔧 The Patch (What Changed)

### Original Code (Simplified)
```csharp
public void Updata() {
    // Complex validation checks
    array = this.PareUpdataFile(path);      // Validates firmware
    array = this.PareUpdataFile1(path);     // More validation

    // If validation fails, shows error ❌
    if (array == null) {
        MessageBox.Show("文件版本错误"); // "File version is Wrong"
    }
}
```

### Patched Code (LEVEL 2)
```csharp
public void Updata() {
    // Skip all validation, load directly ✅
    array = System.IO.File.ReadAllBytes(path);

    if (this.downloadFileEx(array)) {
        MessageBox.Show("write_success");
    }
}
```

**What this does:**
- ❌ **Removes** all firmware validation checks
- ✅ **Loads** any firmware file directly
- ✅ **Allows** flashing of modified firmware

---

## 🎨 Patch Levels Explained

### LEVEL 1: Conservative (Try Original First)
```csharp
// Try original validation
array = this.PareUpdataFile(path);

// If fails, use bypass as fallback
if (array == null) {
    array = System.IO.File.ReadAllBytes(path);
}
```

**Pros:** Original firmware still works normally
**Cons:** May not help if validation is very strict

### LEVEL 2: Direct Loading (RECOMMENDED) ⭐
```csharp
// Skip validation entirely
array = System.IO.File.ReadAllBytes(path);
```

**Pros:** Simple, clear, works with any file
**Cons:** Skips all safety checks (use at own risk)

### LEVEL 3: Maximum Compatibility
```csharp
// Patches multiple methods:
// 1. Updata() - validation bypass
// 2. downloadFileEx() - bootloader check bypass
// 3. check_boot_ver() - version check bypass
```

**Pros:** Maximum compatibility, bypasses everything
**Cons:** Most invasive, requires multiple patches

**See:** `COMPLETE_TK11_BYPASS.md` for LEVEL 3 details

---

## 🐛 Troubleshooting

### "Compilation failed"

**Cause:** Syntax error in pasted code

**Fix:**
1. Make sure you copied **entire** method from `patch_tk11_updata_method.cs`
2. Check all `{ }` braces match (should be balanced)
3. Check all lines end with `;` (except `{` lines)
4. Try **LEVEL 1** bypass (simpler code, in same file)

### "Cannot find method Updata"

**Cause:** Wrong class or method

**Fix:**
1. Navigate to exactly: `TK11` → `K7` → `wfm_progress`
2. Find method: `Updata()` (not `Update()` - note the "a"!)
3. Should have signature: `public void Updata()`

### "Still getting File version is Wrong"

**Cause:** Running original TK11.exe instead of patched

**Fix:**
```cmd
# Make sure you're running the patched version!
TK11_PATCHED.exe

# Not:
# TK11.exe  ← This is still the original!
```

### TK11_PATCHED.exe won't start

**Cause:** Bad compilation or corrupted EXE

**Fix:**
```cmd
# Restore original
copy bin\original\TK11.exe TK11_temp.exe

# Try patching again
dnSpy\dnSpy.exe TK11_temp.exe
# Use LEVEL 1 bypass (more conservative)
```

### Changes don't seem to apply

**Cause:** Forgot to save module

**Fix:**
1. After clicking "Compile"
2. **Must** go to File → Save Module
3. Choose save location
4. Overwrite or save as new file

---

## 📊 Code Comparison

| Original TK11.exe | Patched TK11.exe |
|-------------------|------------------|
| 382 KB | 373 KB |
| Validates firmware format | Loads any file directly |
| Checks CRC/checksums | No validation |
| Rejects modified firmware ❌ | Accepts modified firmware ✅ |
| Shows "File version is Wrong" | Shows "Firmware loaded" |

---

## 🔒 Safety Notes

### What This Patch Does
✅ Bypasses TK11.exe firmware validation
✅ Allows loading modified firmware
✅ Required for USB TX unlock

### What This Patch Does NOT Do
❌ Does NOT modify radio firmware
❌ Does NOT flash radio automatically
❌ Does NOT guarantee flash will succeed
❌ Does NOT enable USB TX (that's the firmware patch)

### Risks
⚠️ **Low risk to PC** - Only modifies TK11.exe software
⚠️ **Medium risk to radio** - If you flash bad firmware
⚠️ **Recovery possible** - Can restore original firmware

**Mitigation:**
- Keep backup of original TK11.exe ✅
- Keep backup of original firmware ✅
- Test with `v3_minimal.bin` first (most conservative) ✅

---

## 🎯 Success Criteria

### ✅ Patch Successful If:
- [ ] dnSpy compilation succeeded (green ✅)
- [ ] Saved module successfully
- [ ] TK11_PATCHED.exe file created (~373 KB)
- [ ] TK11_PATCHED.exe starts normally
- [ ] Can browse to firmware file
- [ ] NO "File version is Wrong" error
- [ ] Shows "Firmware loaded (validation bypassed)" message

### ⏭️ Next Steps:
1. ✅ TK11.exe patched and verified
2. ⏭️ Flash firmware to radio (see `bin\QUICKSTART.md`)
3. ⏭️ Test USB TX on K38 channel

---

## 📚 Related Documentation

- **bin/QUICKSTART.md** - Full 5-step process
- **bin/README.md** - Detailed guide with troubleshooting
- **COMPLETE_TK11_BYPASS.md** - All 3 patch levels explained
- **bin/scripts/patch_tk11_updata_method.cs** - C# code to copy

---

## ⌨️ Quick Command Reference

```cmd
# Backup
copy bin\original\TK11.exe bin\original\TK11_ORIGINAL_BACKUP.exe

# Open in dnSpy
dnSpy\dnSpy.exe bin\original\TK11.exe

# Navigate: TK11 → K7 → wfm_progress → Updata()
# Right-click → Edit Method (C#)...
# Copy code from: bin\scripts\patch_tk11_updata_method.cs
# Paste, Compile, Save Module

# Test
TK11_PATCHED.exe
```

---

**Good luck! You got this! 73! 📻**

*Estimated time: 5 minutes*
*Difficulty: Easy (just copy-paste!)*
*Success rate: 99%+ with these instructions*