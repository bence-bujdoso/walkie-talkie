# dnSpy - Step by Step Patching Instructions

## You Found: "文件版本错误/File version is Wrong"

This is a resource string (error message text). Now we need to find WHERE in the code it's used.

---

## STEP 1: Find Code That Uses This String

### In dnSpy:

1. **Right-click** on the string "File version is Wrong"
2. Select **"Analyze"** from the menu
3. In the Analyzer window (bottom), expand the tree
4. Look for **"Used By"** → This shows which methods use this string
5. **Double-click** on the method that uses it

**OR Alternative Method:**

1. In the left pane (Assembly Explorer), expand the tree:
   - TK11.exe
   - → (namespace name)
   - → → (class names)

2. Look for classes related to firmware loading, such as:
   - `FirmwareLoader`
   - `UpdateFirmware`
   - `LoadFirmware`
   - `FirmwareValidation`
   - `MainForm` or similar

3. Click through methods until you find one that contains the error message

---

## STEP 2: Identify the Validation Code

You're looking for code that looks like this:

### Pattern A: Direct Check
```csharp
if (some_validation_check)
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

### Pattern B: Function Call
```csharp
if (!ValidateFirmware(filename))
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

### Pattern C: Variable Check
```csharp
bool isValid = CheckFirmwareVersion(data);
if (!isValid)
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

**IMPORTANT: Take a screenshot or copy the entire method so I can help you patch it correctly!**

---

## STEP 3: Patch the Code

Once you find the code, you have 3 options:

### Option A: Make the check always FALSE (skip error)

**BEFORE:**
```csharp
if (!ValidateFirmware(filename))
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

**AFTER:**
```csharp
if (false)  // Changed to false - will never show error
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

### Option B: Invert the logic

**BEFORE:**
```csharp
if (!ValidateFirmware(filename))
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

**AFTER:**
```csharp
if (ValidateFirmware(filename))  // Removed the ! (NOT)
{
    // This will never execute now
    // MessageBox.Show("文件版本错误/File version is Wrong");
    // return;
}
```

### Option C: Comment out entirely

**BEFORE:**
```csharp
if (!ValidateFirmware(filename))
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
// Continue with firmware upload...
```

**AFTER:**
```csharp
// Validation disabled
// if (!ValidateFirmware(filename))
// {
//     MessageBox.Show("文件版本错误/File version is Wrong");
//     return;
// }
// Continue with firmware upload...
```

---

## STEP 4: Edit the Code in dnSpy

1. **Right-click** on the METHOD NAME (in the code view)
2. Select **"Edit Method"** or **"Edit IL Instructions"**

### If you choose "Edit Method" (easier):
- You'll see the C# code in an editable window
- Make the changes as shown above
- Click **"Compile"** button at bottom
- If there are errors, fix them or try a simpler change

### If you choose "Edit IL Instructions" (advanced):
- You'll see IL bytecode
- Find the branch instruction (e.g., `brfalse`, `brtrue`)
- Change it or replace with `nop` (no operation)
- This is more complex but more reliable

---

## STEP 5: Save the Patched Executable

1. In dnSpy menu: **File** → **Save Module**
2. Choose a new name: `TK11_PATCHED.exe`
3. Save it to: `E:\AI\tk11\patched_tk11_exe\`

---

## STEP 6: Test the Patched TK11.exe

1. Close all instances of TK11.exe
2. Navigate to: `E:\AI\tk11\`
3. Rename `TK11.exe` → `TK11_ORIGINAL.exe` (backup)
4. Copy `TK11_PATCHED.exe` → `TK11.exe`
5. Launch the new TK11.exe
6. Try to load: `patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin`

**Expected Result:** NO error message, firmware upload should work!

---

## STEP 7: Flash Firmware to Radio

If the patched TK11.exe accepts the firmware:

1. Connect radio to computer
2. Load the patched firmware in TK11.exe
3. Write to radio
4. Test: Select K38 USB channel, press PTT
5. **SUCCESS: No more "DISABLED"!**

---

## Troubleshooting

### "Method failed to compile"
- Try a simpler change (just change `if (!validate)` to `if (false)`)
- Make sure you didn't break the C# syntax

### "Can't save module"
- Run dnSpy as Administrator
- Make sure TK11.exe is not running

### Still getting error after patching
- Make sure you're running the PATCHED exe, not the original
- Check if the patched exe is in the right location

---

## Need Help?

**Please provide:**
1. Screenshot of the code in dnSpy showing the validation check
2. The full method code (copy/paste)
3. Any error messages from dnSpy when trying to compile

I can then give you the EXACT code changes to make!

---

## Quick Reference: What You Need to Find

```csharp
// FIND THIS:
if (some_check_that_returns_false)
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}

// CHANGE TO THIS:
if (false)
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

That's it! The validation is bypassed.
