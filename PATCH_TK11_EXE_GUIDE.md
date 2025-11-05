# TK11.exe Patching Guide - Bypass Firmware Validation

## Problem
TK11.exe validates firmware files and rejects modified firmware with "File version is Wrong!" error.

## Solution
Patch TK11.exe to skip the validation check, allowing upload of our USB TX-enabled firmware.

---

## Method 1: Using dnSpy (Recommended - Easiest)

### Step 1: Download dnSpy
1. Go to: https://github.com/dnSpy/dnSpy/releases
2. Download latest release (e.g., `dnSpy-net-win64.zip`)
3. Extract to a folder

### Step 2: Open TK11.exe
1. Launch `dnSpy.exe`
2. File → Open → Select `TK11.exe`
3. You'll see the decompiled C# code

### Step 3: Find the Validation Function
1. Press `Ctrl+Shift+K` to open Search
2. Search for: `File version is Wrong`
3. Double-click the result to view the code
4. You'll see something like:

```csharp
if (!ValidateFirmware(filename))
{
    MessageBox.Show("File version is Wrong!");
    return;
}
```

### Step 4: Patch the Code
**Option A: Make validation always succeed**
```csharp
// Change this:
if (!ValidateFirmware(filename))

// To this:
if (false) // Always skip this error
```

**Option B: Comment out the validation**
```csharp
// Simply comment out or delete the validation check entirely
// if (!ValidateFirmware(filename))
// {
//     MessageBox.Show("File version is Wrong!");
//     return;
// }
```

### Step 5: Compile and Save
1. Right-click on the modified method
2. Select "Compile"
3. File → Save Module
4. Save as `TK11_PATCHED.exe`

### Step 6: Test
1. Close original TK11.exe
2. Rename `TK11.exe` to `TK11_ORIGINAL.exe` (backup)
3. Rename `TK11_PATCHED.exe` to `TK11.exe`
4. Try loading our patched firmware!

---

## Method 2: Using ILSpy (Alternative)

### Download
https://github.com/icsharpcode/ILSpy/releases

### Steps
1. Open TK11.exe in ILSpy
2. Search for "File version is Wrong"
3. Export to C# project
4. Edit the code to skip validation
5. Recompile with Visual Studio or `csc.exe`

---

## Method 3: Hex Patching (Advanced)

If you know assembly/IL, you can hex edit the .NET IL bytecode directly:

1. Find the validation function's IL code
2. Replace the conditional branch with `nop` (0x00) instructions
3. Or change `brfalse` to `br` (always branch)

This requires understanding .NET IL opcodes.

---

## What We're Looking For

The validation code likely looks like one of these:

### Pattern 1: Simple Checksum
```csharp
bool ValidateFirmware(string path)
{
    byte[] data = File.ReadAllBytes(path);
    uint checksum = CalculateChecksum(data);
    uint expected = ReadStoredChecksum(data);
    return checksum == expected;
}
```

### Pattern 2: Cryptographic Signature
```csharp
bool ValidateFirmware(string path)
{
    byte[] data = File.ReadAllBytes(path);
    byte[] signature = ReadSignature(data);
    return VerifySignature(data, signature, publicKey);
}
```

### Pattern 3: Version Check
```csharp
bool ValidateFirmware(string path)
{
    string version = ReadFirmwareVersion(path);
    return version == "5.00.09";
}
```

**We want to make ANY of these return `true` always, or skip the check entirely.**

---

## After Patching TK11.exe

Once you have the patched `TK11.exe`:

1. Use it to load: `TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin`
2. Upload to radio
3. Select K38 USB channel
4. Press PTT - should transmit!

---

## Alternative: Try Different Firmware Files

If patching the exe doesn't work, try these already-created firmwares:

```
E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin
E:\AI\tk11\patched_firmware\TK11_PATCHED_CHECKSUM_FIXED.bin
```

Both have the USB TX patch applied at offset 0x314D (0x03 → 0x13).

---

## Troubleshooting

**Q: dnSpy shows errors when compiling?**
A: Make sure you're only changing the `if` condition, not the entire method structure

**Q: Patched exe crashes?**
A: The modification might have broken something. Try a simpler patch (just change `if (!validate)` to `if (false)`)

**Q: Still getting "File version is Wrong!" after patching?**
A: Make sure you're running the patched exe, not the original

**Q: Can't save in dnSpy?**
A: Run dnSpy as Administrator

---

## Safety Notes

- ⚠️ Backup original TK11.exe before patching
- ⚠️ Backup original firmware before flashing
- ⚠️ Test with dummy load first!
- ⚠️ Modifying radio firmware can brick the device
- ⚠️ May void warranty
- ⚠️ Ensure compliance with local radio regulations

---

## Files Prepared

Original firmware: `E:\AI\tk11\TK11_v5.00.09_ENG.bin`
Patched firmware: `E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin`
Backup of TK11.exe: `E:\AI\tk11\TK11_ORIGINAL_BACKUP.exe`

The patched firmware has:
- USB TX enabled (0x13 at offset 0x314D)
- All other bytes identical to original
- Ready to flash once TK11.exe validation is bypassed
