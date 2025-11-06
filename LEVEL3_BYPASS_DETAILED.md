# TK11.exe Level 3 Bypass - Detailed Instructions

## ⚠️ When to Use Level 3 Bypass

Use this ONLY if:
- ✅ You successfully patched TK11.exe (Level 1-2 bypass)
- ✅ Patched firmware loads WITHOUT "File version is Wrong" error
- ❌ BUT you get **"Write Fail"** error when trying to flash
- ❌ ALL 8 firmware variants give "Write Fail"

## 🎯 What Level 3 Does

Level 3 patches the **bootloader handshake check** in the `downloadFileEx()` method:
- The bootloader validates the firmware format
- If validation fails, it returns an error
- TK11.exe stops flashing and shows "Write Fail"
- **Level 3 bypass:** Forces the handshake to succeed even if the bootloader rejects it

## 📝 Step-by-Step Instructions

### Prerequisites
- You already have `TK11_PATCHED.exe` from Level 1-2 bypass
- dnSpy is installed and ready

### Step 1: Open Your Patched TK11.exe in dnSpy

1. Start dnSpy
2. File → Open
3. Select: `bin/patched_software/TK11_PATCHED.exe`

### Step 2: Find the downloadFileEx() Method

In the left tree view, navigate to:
```
TK11
└─ K7
   └─ wfm_progress
      └─ downloadFileEx(byte[] allBuffer)  ← Find this method
```

### Step 3: Edit the Method

1. **Right-click** on `downloadFileEx(byte[] allBuffer)`
2. Select **"Edit Method (C#)..."**
3. A code editor window will open with the full method code

### Step 4: Find the Bootloader Check

Scroll down and find this section (around line 20-40):

```csharp
bool flag2 = false;
if (protocol_struct.check_boot_ver(protocol_struct.boot_version))
{
    Random random = new Random();
    wfm_progress.seed = random.Next(0, 16);
    for (int i = 0; i < 5; i++)
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
    if (!flag2)  // ⭐ THIS IS THE PROBLEM LINE
    {
        return false;  // ⭐ THIS CAUSES "Write Fail"
    }
```

### Step 5: Apply the Bypass

Find this specific block:

```csharp
if (!flag2)
{
    return false;
}
```

**Replace it with:**

```csharp
if (!flag2)
{
    // ⭐ LEVEL 3 BYPASS: Force bootloader handshake success
    flag2 = true;
    System.Windows.Forms.MessageBox.Show(
        "Bootloader handshake bypassed!\n" +
        "Continuing with flash process...",
        "TK11 Level 3 Bypass Active",
        System.Windows.Forms.MessageBoxButtons.OK,
        System.Windows.Forms.MessageBoxIcon.Warning
    );
}
```

### Step 6: Compile

1. Click the **"Compile"** button (bottom right of editor)
2. Wait for compilation
3. If successful, you'll see "Compilation successful"
4. If errors, check for typos and try again

### Step 7: Save as Level 3 Version

1. **File** → **Save Module**
2. Save as: `bin/patched_software/TK11_PATCHED_LEVEL3.exe`
3. Close dnSpy

### Step 8: Test with Level 3 Bypass

1. Run `TK11_PATCHED_LEVEL3.exe`
2. Load any patched firmware (try v3_minimal again)
3. Click "Update" to flash
4. **Expected behavior:**
   - You'll see a popup: "Bootloader handshake bypassed!"
   - Flash process should continue
   - Progress bar should move
5. **Success indicator:** Flash reaches 100% and radio restarts

## 🔧 Alternative Approach (Simpler)

If the above code is too complex, you can simply **comment out** the return statement:

Find:
```csharp
if (!flag2)
{
    return false;
}
```

Change to:
```csharp
if (!flag2)
{
    // return false;  // ⭐ BYPASSED - Continue anyway
}
```

This is simpler but doesn't give you a notification that the bypass is active.

## ⚠️ Important Warnings

### Risks of Level 3 Bypass

1. **Bricking risk:** Bypassing bootloader checks means invalid firmware can be sent to the device
2. **Corruption risk:** If firmware format is wrong, radio may not boot
3. **Recovery needed:** Keep original firmware ready to flash back

### Safety Precautions

Before using Level 3:
- ✅ Test with original firmware first (verify it still works)
- ✅ Have original firmware file ready
- ✅ Make sure battery is fully charged
- ✅ Don't disconnect during flash
- ✅ Be prepared to flash original firmware back if needed

## 🔍 Troubleshooting

### "Still getting Write Fail"

**Possible causes:**
1. You're not running TK11_PATCHED_LEVEL3.exe (check filename)
2. The bypass code wasn't compiled correctly (check for errors)
3. There's another check elsewhere in the code

**Debug steps:**
1. Verify you see the "Bootloader handshake bypassed!" popup
2. If no popup appears, the bypass didn't work
3. Try the "alternative approach" (comment out return statement)

### Flash Starts but Fails at X%

**Cause:** Firmware format is fundamentally incompatible

**Solution:** We need to decrypt the firmware first, then patch it
- This requires extracting the decryption algorithm from TK11.exe
- Much more complex, but may be necessary

### Radio Won't Boot After Flash

**RECOVERY:**
1. Enter bootloader mode again
2. Flash original firmware: `TK11_v5.00.09_ENG.bin`
3. Radio should boot normally
4. Try a different approach

## 📊 Success Probability

| Scenario | Probability | Notes |
|----------|-------------|-------|
| Level 3 fixes "Write Fail" | **60%** | If firmware format is close to valid |
| Flash completes to 100% | **50%** | Depends on firmware structure |
| Radio boots after flash | **40%** | May need decrypted firmware approach |
| USB TX works if it boots | **95%** | Patch is in the right place |

## 🆘 If Level 3 Doesn't Work

If Level 3 bypass still fails, we need to:

1. **Decrypt the original firmware first**
   - Extract decryption algorithm from TK11.exe
   - Decrypt `TK11_v5.00.09_ENG.bin`
   - Patch the DECRYPTED firmware
   - Test with Level 3 bypass (send raw decrypted firmware)

2. **OR: Reverse engineer the firmware format**
   - Analyze exactly what the bootloader expects
   - Reconstruct proper header/wrapper
   - Re-encrypt if necessary

Both approaches are significantly more complex and time-consuming.

## ✅ Success Checklist

After applying Level 3 bypass:
- [ ] TK11_PATCHED_LEVEL3.exe created
- [ ] Method compiled successfully
- [ ] See "Bootloader handshake bypassed!" popup when flashing
- [ ] Flash progress bar moves (doesn't get stuck at 0%)
- [ ] Flash reaches 100%
- [ ] Radio restarts automatically
- [ ] Radio boots normally
- [ ] USB TX mode works

## 📞 Next Steps

1. **Try Level 3 bypass** with the instructions above
2. **Report back:** Does the flash progress beyond 0%?
3. **If successful:** Test USB TX mode
4. **If still fails:** We'll need to try the decryption approach

---

**Good luck! 73! 📻**

**Version:** 1.0
**Date:** 2025-11-06
**Status:** Ready to use
