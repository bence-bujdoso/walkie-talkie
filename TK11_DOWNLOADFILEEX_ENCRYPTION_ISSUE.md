# TK11.exe downloadFileEx() - Critical Encryption Issue

## 🔴 PROBLEM IDENTIFIED

The current `downloadFileEx()` method has a **Level 3 bypass** implemented, BUT there's a critical flaw in how it handles encryption after the bypass.

---

## 📋 Current Code Analysis

### The Bypass (Lines ~20-30)
```csharp
bool flag2 = false;
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

// ⚠️ BYPASS: Forces success even if handshake failed
if (!flag2)
{
    flag2 = true;
    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}
```

**Status:** ✅ Bypass is present and working

---

## 🐛 THE BUG

### The Encryption Code (Lines ~35-50)
```csharp
Thread.Sleep(500);

byte[] array2 = new byte[16];  // AES Key
byte[] array3 = new byte[16];  // AES IV

for (int j = 0; j < 16; j++)
{
    array2[j] = Util.updatakey[wfm_progress.seed, j];
    array3[j] = Util.updatakey[wfm_progress.seed, j + 16];
}

// ⚠️ CRITICAL: Uses bootloader response to modify IV
for (i = 0; i < array3.Length; i++)
{
    byte[] array5 = array3;
    int num4 = i;
    int num5 = num4;
    array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
    //              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    //              THIS MAY BE NULL OR UNINITIALIZED!
}

// Encrypts firmware with potentially wrong keys
array = Util.AESEncrypt(array, array2, array3);
```

### The Problem

1. **If bootloader handshake succeeds:**
   - `protocol_struct.UpdataConnRsp.u8RandCode` contains valid random data from bootloader
   - IV is properly modified with XOR
   - Encryption works correctly ✅

2. **If bootloader handshake fails (bypassed):**
   - `protocol_struct.UpdataConnRsp.u8RandCode` is **null or uninitialized**
   - XOR operation uses invalid data or throws exception
   - Firmware is encrypted with **wrong keys**
   - Bootloader cannot decrypt firmware
   - **Result: "Write Fail"** ❌

---

## 💡 THE SOLUTION

We need to handle the bypass case properly by ensuring valid encryption keys are used even when the handshake is bypassed.

### Option 1: Use Default Keys When Bypassing (RECOMMENDED)

```csharp
bool flag2 = false;
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

// ⭐ NEW: Track if we bypassed the handshake
bool bypassedHandshake = false;

if (!flag2)
{
    flag2 = true;
    bypassedHandshake = true;  // ⭐ NEW
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

// ⭐ NEW: Only modify IV if handshake succeeded
if (!bypassedHandshake)
{
    for (i = 0; i < array3.Length; i++)
    {
        byte[] array5 = array3;
        int num4 = i;
        int num5 = num4;
        array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
    }
}
// If bypassed, use IV as-is (from updatakey table)

array = Util.AESEncrypt(array, array2, array3);
```

**Effect:** When bypassing, uses base keys from `Util.updatakey` without the XOR modification.

---

### Option 2: Initialize UpdataConnRsp with Default Values

```csharp
if (!flag2)
{
    flag2 = true;

    // ⭐ NEW: Initialize UpdataConnRsp with zeros
    if (protocol_struct.UpdataConnRsp == null)
    {
        protocol_struct.UpdataConnRsp = new UpdateConnRsp();  // Adjust type name
    }
    if (protocol_struct.UpdataConnRsp.u8RandCode == null)
    {
        protocol_struct.UpdataConnRsp.u8RandCode = new byte[16];  // All zeros
    }

    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}
```

**Effect:** XOR with zeros = no change to IV, same result as Option 1.

---

### Option 3: Skip Encryption Entirely When Bypassing

```csharp
bool bypassedHandshake = false;

if (!flag2)
{
    flag2 = true;
    bypassedHandshake = true;
    MessageBox.Show("Bootloader bypass aktív! (No encryption)", "Level 3");
}

Thread.Sleep(500);

// ⭐ NEW: Only encrypt if handshake succeeded
if (!bypassedHandshake)
{
    byte[] array2 = new byte[16];
    byte[] array3 = new byte[16];

    for (int j = 0; j < 16; j++)
    {
        array2[j] = Util.updatakey[wfm_progress.seed, j];
        array3[j] = Util.updatakey[wfm_progress.seed, j + 16];
    }

    for (i = 0; i < array3.Length; i++)
    {
        byte[] array5 = array3;
        int num4 = i;
        int num5 = num4;
        array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
    }

    array = Util.AESEncrypt(array, array2, array3);
}
// Else: Send firmware unencrypted
```

**Effect:** Bypasses encryption entirely, sends raw firmware to bootloader.

---

## 🎯 RECOMMENDED APPROACH

**Use Option 1** - It's the safest and most compatible:

1. ✅ Maintains encryption (bootloader might require it)
2. ✅ Uses predictable keys from `Util.updatakey` table
3. ✅ No risk of null reference exceptions
4. ✅ Minimal code changes
5. ✅ Most likely to be accepted by bootloader

---

## 🔧 Implementation Steps

### 1. Open TK11.exe in dnSpy
```bash
dnSpy\dnSpy.exe TK11.exe
```

### 2. Navigate to the Method
```
TK11
└─ K7
   └─ wfm_progress
      └─ downloadFileEx(byte[] allBuffer)
```

### 3. Right-click → "Edit Method (C#)..."

### 4. Apply the Fix (Option 1)

Find this section:
```csharp
if (!flag2)
{
    flag2 = true;
    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}
```

Replace with:
```csharp
bool bypassedHandshake = false;

if (!flag2)
{
    flag2 = true;
    bypassedHandshake = true;
    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}
```

Then find this section:
```csharp
for (i = 0; i < array3.Length; i++)
{
    byte[] array5 = array3;
    int num4 = i;
    int num5 = num4;
    array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
}
```

Wrap it in a condition:
```csharp
if (!bypassedHandshake)
{
    for (i = 0; i < array3.Length; i++)
    {
        byte[] array5 = array3;
        int num4 = i;
        int num5 = num4;
        array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
    }
}
```

### 5. Compile and Save
- Click "Compile"
- If successful: File → Save Module
- Save as: `TK11_PATCHED_ENCRYPTION_FIXED.exe`

---

## 🧪 Testing

### Before Fix
```
Load firmware → Click Write
↓
Bootloader handshake fails
↓
Bypass activates (flag2 = true)
↓
XOR with uninitialized u8RandCode → Wrong encryption
↓
Send encrypted firmware → Bootloader can't decrypt
↓
Result: "Write Fail" ❌
```

### After Fix
```
Load firmware → Click Write
↓
Bootloader handshake fails
↓
Bypass activates (flag2 = true, bypassedHandshake = true)
↓
Skip XOR modification → Use base keys from updatakey table
↓
Send encrypted firmware → Bootloader can decrypt
↓
Result: "Write Success" ✅
```

---

## 📊 Expected Impact

| Scenario | Before Fix | After Fix |
|----------|------------|-----------|
| Normal handshake works | ✅ Works | ✅ Works |
| Handshake fails, needs bypass | ❌ Write Fail | ✅ Should work |
| Modified firmware | ❌ Write Fail | ✅ Should work |

**Expected result:** Firmware variants should now flash successfully!

---

## ⚠️ Alternative: If Option 1 Doesn't Work

Try **Option 3** (skip encryption entirely):
- Bootloader might accept unencrypted firmware
- Worth testing if Option 1 fails

---

## 🎯 Next Steps

1. ✅ Apply Option 1 fix to TK11.exe
2. ✅ Save as TK11_PATCHED_ENCRYPTION_FIXED.exe
3. ✅ Test with firmware variants
4. ✅ If successful: Flash to radio and verify USB TX
5. ❌ If still fails: Try Option 3 (no encryption)

---

## 📝 Technical Notes

### Why This Bug Exists

The original code was designed for normal operation where:
1. Handshake always succeeds
2. UpdataConnRsp is always valid
3. Encryption keys are always properly initialized

When we added the bypass, we broke this assumption!

### Why It Wasn't Caught Earlier

- Testing may have been done with original firmware (which might have different handshake behavior)
- The bypass message appears, making it seem like it's working
- The actual failure happens later during bootloader decryption
- "Write Fail" error is generic and doesn't specify encryption mismatch

### Bootloader Behavior

The bootloader likely:
1. Receives encrypted firmware packets
2. Attempts decryption with expected keys
3. Verifies decrypted data (CRC, format, etc.)
4. If decryption fails → immediate "Write Fail"
5. If decryption succeeds but format wrong → also "Write Fail"

With the fix, we ensure decryption succeeds, so any remaining failures are format-related (which we're testing with 8 variants).

---

## 🏆 Success Criteria

**This fix is successful if:**
- ✅ Firmware loads without "File version is Wrong" (already working)
- ✅ Bypass message appears (already working)
- ✅ "Write Success" instead of "Write Fail" (NEW!)
- ✅ Radio accepts firmware and restarts
- ✅ USB TX mode works on K38 channel

---

**Priority: HIGH** 🔴

**This is likely THE issue preventing successful firmware flashing!**

**Estimated fix time: 5-10 minutes**

**Test immediately after applying fix!**
