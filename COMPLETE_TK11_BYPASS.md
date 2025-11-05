# Complete TK11.exe Bypass Guide - All Validations Removed

## 🎯 Mission: Skip ALL firmware validation in TK11.exe

This guide provides **3 bypass levels** - choose based on your comfort level.

---

## 📋 Preparation

### 1. Backup Original
```bash
cd E:\AI\tk11
copy TK11.exe TK11_ORIGINAL_BACKUP.exe
```

### 2. Open dnSpy
```bash
dnSpy\dnSpy.exe TK11.exe
```

### 3. Navigate to wfm_progress class
```
TK11
└─ K7
   └─ wfm_progress
```

---

## 🟢 LEVEL 1: Conservative Bypass (RECOMMENDED)

**What it does:** Adds fallback to direct file read if validation fails
**Risk:** LOW
**Compatibility:** Tries original validation first

### Method: wfm_progress.Updata()

**Find this method** in the left pane, right-click → "Edit Method (C#)..."

**REPLACE THE ENTIRE METHOD with:**

```csharp
public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;
        try
        {
            array = this.PareUpdataFile(path);
            wfm_progress.file_ver = "new";
        }
        catch (Exception ex)
        {
            array = null;
            wfm_progress.file_ver = "old";
        }
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
        // ⭐ BYPASS: If validation failed, load directly
        if (array == null)
        {
            try
            {
                array = System.IO.File.ReadAllBytes(path);
                wfm_progress.file_ver = "bypass";
            }
            catch (Exception ex2)
            {
                array = null;
            }
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
            MessageBox.Show(this.GetLang("文件版本错误"));
        }
    }
}
```

**Click "Compile"** → If successful, proceed to save

---

## 🟡 LEVEL 2: Moderate Bypass

**What it does:** Skips validation entirely, loads file directly
**Risk:** LOW
**Compatibility:** Works with any firmware file

### Method: wfm_progress.Updata()

**REPLACE THE ENTIRE METHOD with:**

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
            wfm_progress.file_ver = "direct";
            MessageBox.Show("Firmware loaded (validation bypassed)");
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

**Click "Compile"**

---

## 🔴 LEVEL 3: Aggressive Bypass (Maximum compatibility)

**What it does:** Bypasses validation AND bootloader checks
**Risk:** MEDIUM
**Compatibility:** Maximum - accepts any file, minimal bootloader checks

### Step 3A: Patch wfm_progress.Updata()

Use the **LEVEL 2** code above

### Step 3B: Patch downloadFileEx()

**Find:** `wfm_progress.downloadFileEx` method

**Find this section (around line 20-30):**
```csharp
bool flag2 = false;
if (protocol_struct.check_boot_ver(protocol_struct.boot_version))
{
    Random random = new Random();
    wfm_progress.seed = random.Next(0, 16);
    for (i = 0; i < 5; i++)
    {
        try
        {
            flag2 = protocol_struct.SendUpdataConnectReq(protocol_struct.boot_version, wfm_progress.seed);
        }
        catch (Exception ex)
        {
            flag2 = false;
        }
        if (protocol_struct.boot_version == "4.00.03")
        {
            break;
        }
        if (flag2)
        {
            break;
        }
    }
    if (!flag2)
    {
        return false;  // ⭐ THIS LINE CAUSES REJECTION
    }
```

**CHANGE THE RETURN FALSE to:**
```csharp
    if (!flag2)
    {
        // ⭐ BYPASS: Continue even if bootloader handshake fails
        // return false;
        flag2 = true;  // Force success
    }
```

**OR simply remove the entire check:**
```csharp
    // if (!flag2)
    // {
    //     return false;
    // }
```

**Click "Compile"**

### Step 3C: Patch check_boot_ver() (Optional, for max compatibility)

**Find:** `protocol_struct.check_boot_ver` method (if accessible)

**Change to always return true:**
```csharp
public static bool check_boot_ver(string ver)
{
    return true;  // ⭐ BYPASS: Accept any boot version
}
```

---

## 💾 Save Patched TK11.exe

1. **File** → **Save Module**
2. Save as: `E:\AI\tk11\TK11_PATCHED_COMPLETE.exe`

---

## ✅ Verification

### Test 1: File Loading
```bash
cd E:\AI\tk11
copy TK11_PATCHED_COMPLETE.exe TK11.exe
TK11.exe
```

1. Click "Firmware Update" or similar
2. Browse to: `patched_firmware_final\TK11_PATCHED_v3_minimal.bin`
3. **Expected:** File loads without "File version is Wrong" error ✅

### Test 2: Flash Initiation
1. Click "Update" or "Flash" button
2. **Expected:** Progress bar appears and starts ✅
3. **Watch for:** "Write success" or "Write fail" message

---

## 🔧 Troubleshooting

### "Compilation failed"
**Cause:** Syntax error in code

**Fix:**
- Check all curly braces `{}` match
- Check all semicolons `;` present
- Try simpler patch (Level 1 or Level 2)

### "Still getting File version is Wrong"
**Cause:** Running original TK11.exe, not patched version

**Fix:**
```bash
# Verify you're using patched version
dir TK11.exe
# Date should be recent (today)

# Re-copy if needed
copy TK11_PATCHED_COMPLETE.exe TK11.exe
```

### "Write fail" immediately
**Cause:** Bootloader rejecting firmware format

**Fix:**
- Try different firmware variant (v1, v2, v3, v4)
- Use Level 3 bypass (patches downloadFileEx too)
- Check firmware file is not corrupted

### TK11.exe won't start after patch
**Cause:** Bad compile or corrupted exe

**Fix:**
```bash
# Restore original
copy TK11_ORIGINAL_BACKUP.exe TK11.exe

# Try again with simpler patch (Level 1)
```

---

## 📊 Which Level Should I Use?

| Level | Use If... | Pros | Cons |
|-------|-----------|------|------|
| **Level 1** | First attempt, want safest option | Original validation still works for good firmware | May not help if firmware format wrong |
| **Level 2** | Level 1 didn't work | Simple, clear bypass | Skips all validation |
| **Level 3** | Level 1 & 2 didn't work, "Write fail" error | Maximum compatibility | More complex, more changes |

**Recommendation:** Start with Level 1, escalate if needed.

---

## 🎯 Success Criteria

### ✅ TK11.exe Patch Successful If:
- [ ] dnSpy compiles without errors
- [ ] TK11.exe starts normally
- [ ] Can browse to firmware file
- [ ] NO "File version is Wrong" error
- [ ] Flash process initiates

### ✅ Complete Success If:
- [ ] Flash reaches 100%
- [ ] Radio restarts
- [ ] Radio functions normally
- [ ] USB mode works without "DISABLE"

---

## 🚀 Quick Command Summary

```bash
# 1. Backup
copy TK11.exe TK11_ORIGINAL_BACKUP.exe

# 2. Open dnSpy
dnSpy\dnSpy.exe TK11.exe

# 3. Patch methods (see above)

# 4. Save as TK11_PATCHED_COMPLETE.exe

# 5. Test
copy TK11_PATCHED_COMPLETE.exe TK11.exe
TK11.exe

# 6. Load firmware
# patched_firmware_final\TK11_PATCHED_v3_minimal.bin
```

---

## 📝 Next Steps After Successful Patch

1. ✅ Patched TK11.exe accepts firmware
2. ✅ Test with each firmware variant (v1, v2, v3, v4)
3. ✅ Find which variant radio accepts
4. ✅ Flash to radio
5. ✅ Test USB TX mode
6. ✅ Celebrate! 🎉

**Good luck! 73!** 📻
