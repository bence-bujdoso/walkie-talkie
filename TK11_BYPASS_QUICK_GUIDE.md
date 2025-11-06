# TK11.exe Quick Bypass Guide - "File version is Wrong" Fix

## 🎯 Goal
Fix the "File version is Wrong" error by patching TK11.exe to skip firmware validation.

---

## ⚡ Quick Start (5 minutes)

### Step 1: Backup Original TK11.exe
```bash
# On Windows, navigate to your TK11 folder (e.g., E:\AI\tk11)
copy TK11.exe TK11_ORIGINAL.exe
```

### Step 2: Open dnSpy
```bash
# Start dnSpy (should be in your TK11 folder)
dnSpy\dnSpy.exe
```

### Step 3: Load TK11.exe
1. In dnSpy: **File** → **Open**
2. Select: `TK11.exe`
3. Wait for it to load

### Step 4: Navigate to the Update Method
In the left tree view, expand:
```
TK11
└─ K7
   └─ wfm_progress
      └─ Updata()  ← Find this method
```

### Step 5: Edit the Method
1. **Right-click** on `Updata()` method
2. Select **"Edit Method (C#)..."**
3. A code editor window will open

### Step 6: Replace the Code

**DELETE ALL THE CODE** and replace with this:

```csharp
public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;

        // ⭐ BYPASS: Load firmware directly without validation
        try
        {
            array = System.IO.File.ReadAllBytes(path);
            wfm_progress.file_ver = "bypass";
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error reading file: " + ex.Message);
            array = null;
        }

        if (array != null)
        {
            if (this.downloadFileEx(array))
            {
                MessageBox.Show(this.GetLang("write_success"));
            }
            else
            {
                MessageBox.Show(this.GetLang("write_fail"));
            }
        }
        else
        {
            MessageBox.Show("Could not read firmware file");
        }
    }
}
```

### Step 7: Compile
1. Click **"Compile"** button (bottom right)
2. Wait for compilation
3. If successful, you'll see "Compilation successful" or similar
4. If errors, check for typos and try again

### Step 8: Save Patched TK11.exe
1. **File** → **Save Module**
2. Save as: `TK11_PATCHED.exe` (in the same folder)
3. Close dnSpy

### Step 9: Test the Patched Version
```bash
# Backup current TK11.exe
copy TK11.exe TK11_ORIGINAL_BACKUP.exe

# Use the patched version
copy TK11_PATCHED.exe TK11.exe

# Start TK11
TK11.exe
```

### Step 10: Try Loading Your Patched Firmware
1. In TK11.exe, click **"Update"** or **"Firmware Update"**
2. Browse to your patched firmware file (e.g., `TK11_PATCHED_v3_minimal.bin`)
3. Click **"Open"**
4. **Expected Result:** File loads WITHOUT "File version is Wrong" error ✅

---

## 🔍 Troubleshooting

### "Compilation failed"
**Fix:** Check for typos. Copy the code again carefully.

### Still getting "File version is Wrong"
**Fix:** You're running the original TK11.exe, not the patched one.
```bash
# Make sure you copied the patched version:
copy TK11_PATCHED.exe TK11.exe
```

### "Write fail" error after loading
**Fix:** This means the firmware format is still not accepted by the bootloader.
- Try different patched firmware variants (v1, v2, v3, v4)
- OR use **Level 3 bypass** (see Advanced section below)

### TK11.exe won't start
**Fix:** Restore original:
```bash
copy TK11_ORIGINAL_BACKUP.exe TK11.exe
```

---

## 🔥 Advanced: Level 3 Bypass (If Still Problems)

If you still get "Write fail" after loading the firmware, you need **Level 3 bypass**.

### Additional Patch: downloadFileEx Method

After patching `Updata()`, also patch `downloadFileEx()`:

1. In dnSpy, find: `K7` → `wfm_progress` → `downloadFileEx(byte[] allBuffer)`
2. Right-click → **"Edit Method (C#)..."**
3. Find this code (around line 20-30):

```csharp
if (!flag2)
{
    return false;  // ⭐ This causes rejection
}
```

4. **Change it to:**

```csharp
if (!flag2)
{
    flag2 = true;  // ⭐ BYPASS: Force success
}
```

5. Click **"Compile"**
6. **File** → **Save Module** as `TK11_PATCHED_LEVEL3.exe`

---

## ✅ Success Checklist

After patching:
- [ ] TK11.exe starts normally
- [ ] Can browse to firmware file
- [ ] NO "File version is Wrong" error when opening file
- [ ] Flash process starts (progress bar appears)
- [ ] Flash completes to 100%
- [ ] Radio restarts
- [ ] USB TX works (no "DISABLE" message)

---

## 📝 Which Patched Firmware to Try?

Test them in this order:

1. **TK11_PATCHED_v3_minimal.bin** (most conservative, only 1 byte changed)
2. **TK11_PATCHED_v1_simple_crc16xmodem.bin** (includes CRC fix)
3. **TK11_PATCHED_v4_end_of_file.bin** (CRC at end of file)
4. Try other v4 variants if needed

---

## 🎯 Summary

**Problem:** All patched firmware files show "File version is Wrong"

**Root Cause:** TK11.exe validates firmware format/CRC before loading

**Solution:** Patch TK11.exe to skip validation and load firmware directly

**Steps:**
1. Open TK11.exe in dnSpy
2. Edit `Updata()` method to bypass validation
3. Save as TK11_PATCHED.exe
4. Use patched version to load your patched firmware
5. Flash to radio

**Result:** Patched firmware can be loaded and flashed to radio ✅

---

## 📞 Need Help?

If this doesn't work:
1. Make sure you're using the PATCHED TK11.exe
2. Try all 8 firmware variants
3. Use Level 3 bypass if needed
4. Check that original firmware still works (to verify radio/cable OK)

Good luck! 73! 📻
