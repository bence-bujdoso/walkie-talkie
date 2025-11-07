# CRITICAL TESTS - Determine Root Cause

## 🚨 Two Different Issues Identified

1. **Firmware patch value:** Using 0x13 instead of 0x17
2. **Encryption/Format:** Bootloader rejecting during flash

We need to determine which is causing the "Write Fail".

---

## 🧪 TEST #1: Verify Bypass Works with ORIGINAL Firmware (CRITICAL!)

**This will tell us if the encryption/bypass is working at all.**

### Steps:

1. **Open TK11.exe** (with encryption fix applied)
2. **Load:** `TK11_v5.00.09_ENG.bin` (the ORIGINAL, unmodified firmware)
3. **Connect radio**
4. **Click "Write"**

### Expected Results:

#### If "Write Success" ✅
- **Good news:** Encryption fix is working!
- **Diagnosis:** The patched firmware FORMAT is wrong
- **Next:** Test no-encryption approach with patched firmware

#### If "Write Fail" ❌
- **Bad news:** Encryption is still wrong even for original firmware
- **Diagnosis:** Need to skip encryption entirely when bypassing
- **Next:** Apply no-encryption modification immediately

---

## 🧪 TEST #2: Try No-Encryption Approach

**If TEST #1 fails OR if original firmware works but patched doesn't:**

### Apply This Modification to downloadFileEx():

Replace your current encryption section with this:

```csharp
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
// If bypassed, skip encryption entirely
```

**Effect:** When bypassing, firmware is sent UNENCRYPTED.

---

## 🐛 THE 0x13 vs 0x17 PATCH VALUE ISSUE

**Separate issue that might prevent USB TX even if flash succeeds!**

### The Bug:

Your firmware patches use **0x13**, but USB mode requires **0x17**!

```
0x13 = 00010011 binary
  Bit 0 (0x01): FM ✓
  Bit 1 (0x02): AM ✓
  Bit 2 (0x04): USB ✗ (NOT SET - BUG!)
  Bit 4 (0x10): WFM ✓

0x17 = 00010111 binary
  Bit 0 (0x01): FM ✓
  Bit 1 (0x02): AM ✓
  Bit 2 (0x04): USB ✓ (NOW SET!)
  Bit 4 (0x10): WFM ✓
```

### Quick Fix:

Edit `create_perfect_firmware.py`:

**Find all instances of:**
```python
data[0x314D] = 0x13
```

**Change to:**
```python
data[0x314D] = 0x17
```

**Then recreate all firmware variants:**
```bash
python create_perfect_firmware.py
```

---

## 📋 RECOMMENDED ACTION PLAN

### Step 1: TEST ORIGINAL FIRMWARE (5 minutes)
```
Load: TK11_v5.00.09_ENG.bin
Test with current TK11.exe
Result: Success or Fail?
```

### Step 2A: If Original Works
```
→ Encryption is working ✅
→ Patched firmware format is wrong
→ Try no-encryption with patched firmware
→ Also fix 0x13 → 0x17 and recreate firmwares
```

### Step 2B: If Original Fails
```
→ Encryption is broken even for original ❌
→ Apply no-encryption modification immediately
→ Test original firmware again (should work)
→ Then fix 0x13 → 0x17 and recreate firmwares
→ Test patched firmwares with no-encryption
```

---

## 🎯 Most Likely Scenario

Based on quick "Write Fail" with multiple variants:

**THEORY:** Bootloader expects **NO ENCRYPTION** when handshake is bypassed.

**Why:**
- Normal mode: Handshake succeeds → Keys negotiated → Encrypted transfer
- Bypass mode: No handshake → No key negotiation → Unencrypted transfer

**This explains:**
- Why multiple firmware variants all fail identically
- Why failure is quick (encryption mismatch detected immediately)
- Why CRC variants don't matter (bootloader can't decrypt to check CRC)

---

## 🚀 IMMEDIATE ACTIONS

**RIGHT NOW - Do in this order:**

1. **Test original firmware** with current TK11.exe
   - Takes 2 minutes
   - Will tell us if encryption works at all

2. **If original fails:**
   - Apply no-encryption modification
   - Recompile and test
   - Should fix the issue

3. **Fix the 0x13 → 0x17 bug:**
   - Edit create_perfect_firmware.py
   - Regenerate all firmware variants
   - Test again

4. **Expected outcome:**
   - No-encryption works
   - Firmware flashes successfully
   - BUT: USB TX might not work if still using 0x13
   - Must use 0x17 for USB TX to actually function

---

## 📊 Diagnosis Summary

| Symptom | Diagnosis | Solution |
|---------|-----------|----------|
| Multiple CRC variants fail identically | Not a CRC issue | Try no-encryption |
| Quick rejection (1 second) | Early validation failure | Test original firmware |
| Encryption fix applied | May still be wrong approach | Skip encryption when bypassing |
| Firmware uses 0x13 | Wrong patch value | Change to 0x17 |

---

## ⚡ QUICK TEST SCRIPT

```
Test 1: Original firmware with current TK11.exe
→ Success? → Encryption works, format is wrong
→ Fail? → Encryption is wrong

Test 2: Apply no-encryption modification
→ Test original firmware → Should work now
→ Test patched firmware (0x13) → May flash but USB won't work
→ Fix to 0x17 and test → Should work completely

Expected time: 15-30 minutes to success
```

---

**Start with TEST #1 (original firmware) and report back immediately!**

This will tell us exactly what the issue is.
