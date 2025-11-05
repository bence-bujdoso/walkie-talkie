# FINAL dnSpy Instructions - Complete the TK11 Firmware Patch

## What We Found

Using .NET reflection, I've identified the exact class that handles firmware validation:

**Class: `K7.wfm_firmware`**

This is the firmware upload window form. It contains all the validation logic.

## Step-by-Step dnSpy Instructions

### 1. Launch dnSpy

```bash
cd E:\AI\tk11
dnSpy/dnSpy.exe
```

### 2. Open TK11.exe

1. File → Open
2. Select: `TK11.exe`
3. Wait for decompilation to complete

### 3. Navigate to the Firmware Class

In the left pane (Assembly Explorer):

```
TK11 (1.0.0.0)
└── K7 (namespace)
    └── wfm_firmware (class) ← **CLICK THIS**
```

### 4. Find the Validation Method

Look for methods in the `wfm_firmware` class that contain:
- "File version is Wrong" or "文件版本错误"
- File reading/checking logic
- Methods like:
  - `wfm_firmware_Load` (probably opens file)
  - `button_Click` or `btnUpdate_Click` (upload button)
  - `ValidateFirmware` or similar
  - `CheckVersion` or similar

**TIP:** Use `Ctrl+Shift+K` to search for "File version is Wrong" - it will show you exactly which method contains this error message.

### 5. Examine the Validation Code

Once you find the method, look for patterns like:

#### Pattern A: Direct Version Check
```csharp
byte[] firmwareData = File.ReadAllBytes(filename);

// Check bytes at specific offset
if (firmwareData[0x20] != 0x05 ||
    firmwareData[0x21] != 0x00 ||
    firmwareData[0x22] != 0x00 ||
    firmwareData[0x23] != 0x09)
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

#### Pattern B: Checksum Validation
```csharp
uint calculatedChecksum = CalculateChecksum(firmwareData);
uint storedChecksum = BitConverter.ToUInt32(firmwareData, 0x0C);

if (calculatedChecksum != storedChecksum)
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

#### Pattern C: Version String Check
```csharp
string version = Encoding.ASCII.GetString(firmwareData, offset, length);

if (version != "5.00.09")
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
```

### 6. Two Patching Strategies

#### Strategy A: Skip Validation Entirely (EASIEST)

Find the validation check and make it always pass:

**BEFORE:**
```csharp
if (!ValidateFirmware(filename))
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
// Continue with upload
```

**AFTER:**
```csharp
if (false)  // Changed to false - will never execute
{
    MessageBox.Show("文件版本错误/File version is Wrong");
    return;
}
// Continue with upload
```

**How to do it in dnSpy:**
1. Right-click on the method name
2. Select "Edit Method (C#)..."
3. Change the `if` condition to `if (false)`
4. Click "Compile"
5. File → Save Module → Save as `TK11_PATCHED_FINAL.exe`

#### Strategy B: Implement Correct Checksum (ADVANCED)

If you can see the checksum calculation code:

1. Copy the checksum algorithm from dnSpy
2. Implement it in Python (I can help with this)
3. Calculate correct checksum for patched firmware
4. Inject correct checksum into patched firmware

### 7. Save the Patched Executable

1. File → Save Module
2. Save as: `patched_tk11_exe/TK11_PATCHED_FINAL.exe`
3. Close dnSpy

### 8. Test the Patched TK11.exe

```bash
# Backup original
cp TK11.exe TK11_ORIGINAL_BACKUP_FINAL.exe

# Replace with patched version
cp patched_tk11_exe/TK11_PATCHED_FINAL.exe TK11.exe

# Test
./TK11.exe
# Try to load: patched_firmware/TK11_PATCHED_USB_TX_ENABLED_*.bin
```

## What to Look For

When you open the validation method in dnSpy, **TAKE A SCREENSHOT** or **COPY THE ENTIRE METHOD** and share it. I need to see:

1. How the firmware file is read
2. What specific checks are performed
3. Which offsets are checked
4. What the expected values are
5. If there's a checksum calculation, what algorithm is used

## Expected Outcome

If you successfully patch the validation check:
- TK11.exe will accept the modified firmware
- You can upload `TK11_PATCHED_USB_TX_ENABLED_*.bin` to the radio
- The USB TX mode will be unlocked
- K38 channel should transmit without "DISABLE" message

## Troubleshooting

### "Method failed to compile"
- Make sure you only changed the `if` condition
- Try simpler change: `if (false)` instead of commenting out

### "Can't save module"
- Run dnSpy as Administrator
- Close all instances of TK11.exe first

### Still getting error after patching
- Make sure you're running the PATCHED exe
- Check that it's in the correct directory
- Verify the file size changed (should be slightly different)

## Alternative If dnSpy Fails

If dnSpy doesn't work or is too complex, there are already patched versions:

```
patched_tk11_exe/TK11_PATCHED_NOVERCHECK_20251029_170242.exe
patched_tk11_exe/TK11_PATCHED_NOVERCHECK_20251029_170355.exe
```

Try these! They might already have the validation bypassed.

##Test Command

```bash
# Try existing patched version
cp patched_tk11_exe/TK11_PATCHED_NOVERCHECK_20251029_170355.exe TK11_TEST.exe
./TK11_TEST.exe
```

## Files Ready for Testing

**Patched Firmware:**
- `patched_firmware/TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin`
- Contains USB TX unlock (0x03 → 0x13 at offset 0x314D)

**Configuration Files:**
- `TK11_K38_MODE_01_20251029_150652.dat` - AM mode (WORKS NOW)
- `TK11_K38_MODE_04_*.dat` - USB mode (will work after firmware flash)

## Summary

1. **CRITICAL CLASS:** `K7.wfm_firmware`
2. **SEARCH FOR:** "File version is Wrong"
3. **PATCH:** Change validation check to `if (false)`
4. **SAVE:** As TK11_PATCHED_FINAL.exe
5. **TEST:** Load patched firmware

## Next Steps

Once you find and patch the validation code:

1. **Take a screenshot** of the validation method
2. Share it so I can:
   - Confirm the patch is correct
   - Extract the checksum algorithm if needed
   - Create Python implementation
3. Test the patched TK11.exe
4. Flash the modified firmware
5. Test USB TX on K38 channel
6. **SUCCESS!**

---

**The finish line is close! You just need to use dnSpy to look at K7.wfm_firmware and patch one `if` statement.**

**Good luck! 73!**
