# TK11 CPS Patch Troubleshooting Guide

## 🚨 Problem: Still shows "DISABLE" in USB mode (K38)

You patched the .dat file and wrote it back to the radio, but it still shows "DISABLE" when trying to transmit in USB mode (K38).

---

## 🔍 Step-by-Step Debugging

### Step 1: Verify the Patched File

**Check if your PATCHED .dat file actually contains the patch:**

```bash
python bin/scripts/verify_tk11_patch.py TK11_BACKUP_PATCHED.dat
```

**Expected output:**
```
✅ FILE IS PATCHED!
   Value is 0x13 - USB TX should be ENABLED
```

**If it says "FILE IS NOT PATCHED":**
- The patch script didn't work
- You're checking the wrong file
- Re-run the patch script

---

### Step 2: Re-Read from Radio

**IMPORTANT: Read the configuration BACK from the radio to verify the write worked:**

1. Open TK11.exe
2. Connect radio (normal mode)
3. Click **"Read"** / "Download from radio"
4. Save as: `TK11_READBACK.dat`

**Now verify the readback:**

```bash
python bin/scripts/verify_tk11_patch.py TK11_READBACK.dat
```

**Expected:**
```
✅ FILE IS PATCHED!
```

**If it says "FILE IS NOT PATCHED":**
- ❌ The write didn't work, OR
- ❌ The radio reverted the change, OR
- ❌ The offset is wrong

---

### Step 3: Search for TX Mask Locations

**Maybe the TX mask is in a different location or stored in multiple places:**

```bash
python bin/scripts/search_tx_mask.py TK11_BACKUP.dat
```

This will:
- Search for 0x03 and 0x13 patterns
- Show all potential TX mask locations
- Analyze the context around each location
- Identify candidate bytes that look like TX masks

**Look for:**
- Multiple locations with 0x03 value
- Offset 0x314D should be marked with ⭐
- Other suspicious offsets

---

### Step 4: Check Write Process

**Did you actually WRITE the patched file back to the radio?**

Double-check:
1. ✅ You ran the patch script
2. ✅ It created `TK11_BACKUP_PATCHED.dat`
3. ✅ You opened TK11.exe
4. ✅ You clicked **"Write"** (NOT "Read"!)
5. ✅ You selected `TK11_BACKUP_PATCHED.dat` (NOT the original!)
6. ✅ The write completed successfully
7. ✅ Radio rebooted

**Common mistake:**
- Running "Read" instead of "Write"
- Selecting the wrong file (original instead of patched)
- Not waiting for completion

---

## 🔧 Alternative Offsets to Try

If 0x314D doesn't work, the TX mask might be at a different offset in the CPS .dat file.

**Try these alternative offsets:**

### Offset 1: 0x313D (16 bytes earlier)
```python
#!/usr/bin/env python3
with open('TK11_BACKUP.dat', 'r+b') as f:
    f.seek(0x313D)
    f.write(b'\x13')
print("Patched at 0x313D")
```

### Offset 2: 0x315D (16 bytes later)
```python
#!/usr/bin/env python3
with open('TK11_BACKUP.dat', 'r+b') as f:
    f.seek(0x315D)
    f.write(b'\x13')
print("Patched at 0x315D")
```

### Offset 3: Search and patch ALL 0x03 values

**Warning: This is aggressive!**

```python
#!/usr/bin/env python3
with open('TK11_BACKUP.dat', 'r+b') as f:
    data = bytearray(f.read())

    count = 0
    for i in range(len(data)):
        if data[i] == 0x03:
            # Check if it looks like a TX mask (context)
            if i > 0 and i < len(data) - 1:
                data[i] = 0x13
                count += 1
                print(f"Patched offset 0x{i:04X}")

    f.seek(0)
    f.write(data)

print(f"Patched {count} locations")
```

---

## 🧪 Diagnostic Tests

### Test 1: Check Hex Editor

**Open the PATCHED file in a hex editor:**

**Windows:**
- HxD (free): https://mh-nexus.de/en/hxd/

**Linux/Mac:**
```bash
xxd TK11_BACKUP_PATCHED.dat | grep 314d
```

**You should see:**
```
0000314d: .... 13 ...  <-- Value should be 0x13
```

**If you see 0x03:**
- The patch didn't work
- Wrong file
- Re-patch

---

### Test 2: Compare Files

**Compare original and patched:**

```bash
# Linux/Mac
cmp -l TK11_BACKUP.dat TK11_BACKUP_PATCHED.dat

# Or use a diff tool
diff <(xxd TK11_BACKUP.dat) <(xxd TK11_BACKUP_PATCHED.dat)
```

**You should see:**
```
12622  3 23    <-- Byte 12622 (0x314D) changed from 0x03 to 0x13
```

---

### Test 3: File Size Check

**Both files should be the SAME size:**

```bash
ls -la TK11_BACKUP*.dat
```

**If sizes are different:**
- Something went wrong
- Re-patch from scratch

---

## 🎯 Possible Root Causes

### 1. ❌ Wrong Offset

**Symptom:** Patch in file, but doesn't work on radio

**Cause:** The .dat file has a different memory layout than the firmware

**Solution:**
- Use the search script to find the correct offset
- Try alternative offsets
- Search for all 0x03 values and identify the right one

---

### 2. ❌ Multiple TX Mask Locations

**Symptom:** Patched one location, but radio checks another

**Cause:** TX mask is stored in multiple places

**Solution:**
- Search for all 0x03 values
- Patch all of them
- Use the aggressive patch script

---

### 3. ❌ Radio Has ROM Protection

**Symptom:** Write succeeds, but readback shows original value

**Cause:** Radio has protected memory regions

**Solution:**
- This is hardware-level protection
- CPS method won't work
- Need firmware flash (but that also failed)
- Might need JTAG/hardware modding

---

### 4. ❌ Wrong Mode Setting

**Symptom:** Patch works, but still can't TX

**Cause:** USB mode itself is disabled or misconfigured

**Solution:**
- Check radio settings
- Make sure you're in the correct USB mode (K38)
- Try other USB-related modes

---

### 5. ❌ Hardware Limitation

**Symptom:** Everything patched correctly, but still can't TX

**Cause:** Hardware doesn't support USB TX at all

**Solution:**
- This is unlikely (the "DISABLE" message suggests it's software-blocked)
- But if true, no software patch will help

---

## 📝 Debug Checklist

Go through this checklist step by step:

- [ ] Ran patch script successfully
- [ ] Verified patched file with verify script (shows 0x13)
- [ ] Opened TK11.exe
- [ ] Connected radio in normal mode (not bootloader)
- [ ] Clicked "Write" (not "Read")
- [ ] Selected the PATCHED file
- [ ] Write completed successfully (no errors)
- [ ] Radio rebooted
- [ ] Re-read from radio
- [ ] Verified readback with verify script
- [ ] Readback shows 0x13 at offset 0x314D
- [ ] Checked USB mode (K38) on radio
- [ ] Tried to transmit
- [ ] Still shows "DISABLE"

**If all checkboxes are ✅ and it still doesn't work:**
→ The TX mask is in a different location or there's another protection mechanism

---

## 🆘 Next Steps If Nothing Works

### Option 1: Search-and-Destroy

Run the search script and try patching EVERY location with 0x03:

```bash
python bin/scripts/search_tx_mask.py TK11_BACKUP.dat > search_results.txt
```

Review `search_results.txt` and identify all 0x03 locations. Patch them all.

---

### Option 2: Firmware Disassembly

The TX check might be in the firmware code itself, not just a configuration byte.

Would need to:
1. Extract firmware from radio
2. Disassemble ARM code
3. Find the DISABLE check
4. Patch the firmware code
5. Re-flash

This is much more complex.

---

### Option 3: Hardware Mod

If all software attempts fail, might need:
- JTAG/SWD access
- Direct memory writing
- Hardware bypass of the TX blocking circuit

---

## 📞 Report Back

**Please run these commands and share the output:**

```bash
# 1. Verify your patched file
python bin/scripts/verify_tk11_patch.py TK11_BACKUP_PATCHED.dat

# 2. Re-read from radio and verify
# (After re-reading from radio)
python bin/scripts/verify_tk11_patch.py TK11_READBACK.dat

# 3. Search for TX mask locations
python bin/scripts/search_tx_mask.py TK11_BACKUP.dat
```

Share the output and we'll continue debugging! 🔧

---

**73! 📻**
