# ⚠️ YOUR CODE IS MISSING THE ENCRYPTION FIX!

## Current Status

You're getting "Write Fail" because **the encryption fix has NOT been applied yet**.

Looking at your code, it's still the buggy version that causes encryption mismatch.

---

## 🔴 WHAT'S WRONG IN YOUR CODE

### Your Current Code (Lines 27-53) - BUGGY:

```csharp
bool flag2 = false;                              // ❌ Missing: bypassedHandshake variable
wfm_progress.seed = new Random().Next(0, 16);
for (i = 0; i < 5; i++)
{
    try
    {
        flag2 = protocol_struct.SendUpdataConnectReq(protocol_struct.boot_version, wfm_progress.seed);
    }
    catch (Exception)
    {
        flag2 = false;
    }
    if (protocol_struct.boot_version == "4.00.03" || flag2)
    {
        break;
    }
}
if (!flag2)
{
    flag2 = true;                                // ❌ Missing: bypassedHandshake = true
    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}
Thread.Sleep(500);
byte[] array2 = new byte[16];
byte[] array3 = new byte[16];
for (int j = 0; j < 16; j++)
{
    array2[j] = Util.updatakey[wfm_progress.seed, j];
    array3[j] = Util.updatakey[wfm_progress.seed, j + 16];
}
for (i = 0; i < array3.Length; i++)              // ❌ Missing: if (!bypassedHandshake) wrapper
{
    byte[] array5 = array3;
    int num4 = i;
    int num5 = num4;
    array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];  // ❌ BUG: Uses uninitialized data!
}
array = Util.AESEncrypt(array, array2, array3);
```

**THE BUG:** When bypass activates, `UpdataConnRsp.u8RandCode` is null/uninitialized, causing wrong encryption keys!

---

## ✅ WHAT THE FIXED CODE SHOULD LOOK LIKE

### Fixed Code (Lines 27-53) - CORRECT:

```csharp
bool flag2 = false;
bool bypassedHandshake = false;                  // ✅ ADDED: Track bypass state
wfm_progress.seed = new Random().Next(0, 16);
for (i = 0; i < 5; i++)
{
    try
    {
        flag2 = protocol_struct.SendUpdataConnectReq(protocol_struct.boot_version, wfm_progress.seed);
    }
    catch (Exception)
    {
        flag2 = false;
    }
    if (protocol_struct.boot_version == "4.00.03" || flag2)
    {
        break;
    }
}
if (!flag2)
{
    flag2 = true;
    bypassedHandshake = true;                    // ✅ ADDED: Mark as bypassed
    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}
Thread.Sleep(500);
byte[] array2 = new byte[16];
byte[] array3 = new byte[16];
for (int j = 0; j < 16; j++)
{
    array2[j] = Util.updatakey[wfm_progress.seed, j];
    array3[j] = Util.updatakey[wfm_progress.seed, j + 16];
}
if (!bypassedHandshake)                          // ✅ ADDED: Only XOR if handshake succeeded
{
    for (i = 0; i < array3.Length; i++)
    {
        byte[] array5 = array3;
        int num4 = i;
        int num5 = num4;
        array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
    }
}
array = Util.AESEncrypt(array, array2, array3);
```

---

## 📝 EXACTLY 3 CHANGES NEEDED

### Change #1 (Line ~27):
**ADD THIS LINE:**
```csharp
bool bypassedHandshake = false;
```
**RIGHT AFTER:**
```csharp
bool flag2 = false;
```

### Change #2 (Line ~45):
**ADD THIS LINE:**
```csharp
bypassedHandshake = true;
```
**RIGHT AFTER:**
```csharp
flag2 = true;
```

### Change #3 (Line ~56):
**WRAP THE XOR LOOP:**

**BEFORE:**
```csharp
for (i = 0; i < array3.Length; i++)
{
    byte[] array5 = array3;
    int num4 = i;
    int num5 = num4;
    array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
}
```

**AFTER:**
```csharp
if (!bypassedHandshake)  // ← ADD THIS LINE
{
    for (i = 0; i < array3.Length; i++)
    {
        byte[] array5 = array3;
        int num4 = i;
        int num5 = num4;
        array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
    }
}  // ← ADD THIS CLOSING BRACE
```

---

## 🎯 STEP-BY-STEP IN dnSpy

1. **Open TK11.exe in dnSpy**

2. **Navigate to:** `K7` → `wfm_progress` → `downloadFileEx(byte[] allBuffer)`

3. **Right-click** on the method → **"Edit Method (C#)..."**

4. **Find this line (around line 27):**
   ```csharp
   bool flag2 = false;
   ```

5. **Change it to:**
   ```csharp
   bool flag2 = false;
   bool bypassedHandshake = false;  // ← ADD THIS LINE
   ```

6. **Find this section (around line 44-47):**
   ```csharp
   if (!flag2)
   {
       flag2 = true;
       MessageBox.Show("Bootloader bypass aktív!", "Level 3");
   }
   ```

7. **Change it to:**
   ```csharp
   if (!flag2)
   {
       flag2 = true;
       bypassedHandshake = true;  // ← ADD THIS LINE
       MessageBox.Show("Bootloader bypass aktív!", "Level 3");
   }
   ```

8. **Find this section (around line 56-62):**
   ```csharp
   for (i = 0; i < array3.Length; i++)
   {
       byte[] array5 = array3;
       int num4 = i;
       int num5 = num4;
       array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
   }
   ```

9. **Change it to:**
   ```csharp
   if (!bypassedHandshake)  // ← ADD THIS LINE
   {
       for (i = 0; i < array3.Length; i++)
       {
           byte[] array5 = array3;
           int num4 = i;
           int num5 = num4;
           array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
       }
   }  // ← EXISTING CLOSING BRACE
   ```

10. **Click "Compile"** - Should show no errors

11. **File → Save Module** → Save as `TK11_ENCRYPTION_FIXED.exe`

12. **Copy to your working directory:**
    ```
    copy TK11_ENCRYPTION_FIXED.exe TK11.exe
    ```

13. **Test again!**

---

## ✅ HOW TO VERIFY THE FIX

After applying the changes and compiling:

1. Open the fixed TK11.exe
2. Load your minimal firmware
3. Connect radio and click "Write"
4. You should see "Bootloader bypass aktív!" message
5. **Expected result:** Progress bar completes and shows "Write Success"
6. **If still "Write Fail":** The firmware FORMAT is wrong (not encryption)

---

## 🔍 WHY YOUR CURRENT CODE FAILS

**Your Current Flow:**
```
1. Handshake fails
2. Bypass activates → Shows "Bootloader bypass aktív!"
3. Gets encryption keys from Util.updatakey
4. ❌ Tries to XOR IV with UpdataConnRsp.u8RandCode
5. ❌ But UpdataConnRsp.u8RandCode is NULL (no handshake!)
6. ❌ Either crashes or uses garbage data
7. ❌ Wrong encryption keys used
8. Sends encrypted firmware to bootloader
9. ❌ Bootloader can't decrypt (wrong keys)
10. Result: "Write Fail"
```

**Fixed Flow:**
```
1. Handshake fails
2. Bypass activates → Shows "Bootloader bypass aktív!"
3. Sets bypassedHandshake = true
4. Gets encryption keys from Util.updatakey
5. ✅ Checks: if (!bypassedHandshake) → FALSE, skips XOR
6. ✅ Uses IV as-is (predictable base keys)
7. ✅ Correct encryption keys used
8. Sends encrypted firmware to bootloader
9. ✅ Bootloader CAN decrypt (correct keys)
10. Result: "Write Success" ✅ (if format is correct)
```

---

## 📊 Summary

| What | Status |
|------|--------|
| Bypass activation | ✅ Working (you see the message) |
| Encryption fix | ❌ **NOT APPLIED** (still buggy code) |
| Firmware format | ❓ Unknown (can't test until encryption fixed) |

**YOU MUST APPLY THE 3 CHANGES ABOVE TO FIX THE ENCRYPTION ISSUE!**

---

## 🚨 IMPORTANT

The "Write Fail" you're seeing is happening **BECAUSE of the encryption bug**, not because of the firmware format!

Once you apply the 3 changes above:
- If you still get "Write Fail" → Firmware format issue
- If you get "Write Success" → **SUCCESS!** 🎉

**Apply the fix now and test again!**
