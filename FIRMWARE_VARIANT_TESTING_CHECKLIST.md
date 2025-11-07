# Firmware Variant Testing Checklist

## ✅ Prerequisites

- [x] TK11.exe with encryption fix applied
- [x] Encryption fix verified (bypassedHandshake variable present)
- [x] Radio connected via USB cable
- [x] 8 firmware variants ready in `patched_firmware_final/` folder

---

## 🎯 Testing Procedure

### For Each Firmware Variant:

1. **Open TK11.exe**
2. **Click** firmware update/programming button
3. **Browse** to the firmware file
4. **Load** the firmware
5. **Connect** radio (if not already connected)
6. **Click "Write"** or "Update" button
7. **Observe** the result:
   - Bypass message appears? ✅
   - Progress bar completes?
   - Final message: "Write Success" or "Write Fail"?
8. **Record** result in table below

---

## 📋 Testing Checklist

### Round 1: With Encryption (Current)

| # | Firmware Variant | Tested? | Bypass Shown? | Progress? | Result | Notes |
|---|------------------|---------|---------------|-----------|--------|-------|
| 1 | `v3_minimal.bin` | ✅ | ✅ | ~1 sec | ❌ FAIL | Tested, failed quickly |
| 2 | `v1_simple_crc16xmodem.bin` | ⬜ | | | | **TEST THIS NEXT** |
| 3 | `v4_end_of_file.bin` | ⬜ | | | | CRC at EOF (alt) |
| 4 | `v2_crc16ibm.bin` | ⬜ | | | | CRC16-IBM |
| 5 | `v4_header_0x00.bin` | ⬜ | | | | CRC at offset 0x00 |
| 6 | `v4_header_0x04.bin` | ⬜ | | | | CRC at offset 0x04 |
| 7 | `v4_header_0x08.bin` | ⬜ | | | | CRC at offset 0x08 |
| 8 | `v4_header_0x0C.bin` | ⬜ | | | | CRC at offset 0x0C |

### Round 2: Without Encryption (If Round 1 All Fail)

| # | Firmware Variant | Tested? | Result | Notes |
|---|------------------|---------|--------|-------|
| 1 | `v3_minimal.bin` | ⬜ | | No encryption mod |
| 2 | `v1_simple_crc16xmodem.bin` | ⬜ | | No encryption mod |
| 3 | `v4_end_of_file.bin` | ⬜ | | No encryption mod |
| 4 | `v2_crc16ibm.bin` | ⬜ | | No encryption mod |

---

## 🔍 What to Look For

### Success Indicators ✅
- Progress bar reaches 100%
- Message: "Write Success" or similar
- Radio restarts automatically
- Radio powers back on normally

### Failure Indicators ❌
- Quick failure (~1 second) → Header/CRC issue
- Mid-transfer failure (50%) → Checksum/size issue
- Timeout (>30 seconds) → Communication issue
- Error message popup → Specific error reason

---

## 📊 Expected Outcomes

### Best Case: One Variant Works
```
Test variant #2, #3, or #4
↓
Progress bar completes
↓
"Write Success!" ✅
↓
Radio restarts
↓
Navigate to K38
↓
Select USB mode
↓
Press PTT
↓
No "DISABLE" message! 🎉
```

### If All Encrypted Variants Fail
```
All 8 variants tested → All fail
↓
Apply no-encryption modification
↓
Test Round 2 (no encryption)
↓
One should work
```

### If Nothing Works
```
All variants fail (encrypted + unencrypted)
↓
Need USB traffic capture
↓
Analyze bootloader protocol
↓
Identify exact rejection reason
↓
Create custom firmware format
```

---

## 🎯 Testing Priority Order

**Test in this order** (highest probability first):

1. **v1_simple_crc16xmodem.bin** - Most common CRC algorithm
2. **v4_end_of_file.bin** - Alternative EOF CRC placement
3. **v2_crc16ibm.bin** - CRC16-IBM variant
4. **v4_header_0x04.bin** - Header CRC at +4
5. **v4_header_0x08.bin** - Header CRC at +8
6. **v4_header_0x00.bin** - Header CRC at +0
7. **v4_header_0x0C.bin** - Header CRC at +12

*(v3_minimal already tested and failed)*

---

## ⏱️ Time Estimates

- **Each test:** 2-3 minutes
- **Round 1 (7 remaining):** 15-20 minutes
- **Apply no-encryption mod:** 5 minutes
- **Round 2 (if needed):** 10-15 minutes
- **Total worst case:** 40-45 minutes

---

## 📝 Notes Section

### Test Session 1:
**Date:** ____________
**TK11.exe version:** Encryption fix applied
**Results:**

```
v3_minimal: FAIL (1 second)
v1_simple_crc16xmodem: ____________
v4_end_of_file: ____________
...
```

### Test Session 2 (if needed):
**Date:** ____________
**TK11.exe version:** No encryption
**Results:**

```
v3_minimal: ____________
v1_simple_crc16xmodem: ____________
...
```

---

## 🚨 Important Notes

### During Testing:
- ⚠️ **Don't interrupt** the write process once started
- ⚠️ **Keep radio connected** during entire process
- ⚠️ **Close other USB applications** (device managers, etc.)
- ⚠️ **Use original USB cable** (not a cheap replacement)

### If Radio Becomes Unresponsive:
1. Disconnect USB cable
2. Remove battery
3. Wait 10 seconds
4. Reinsert battery
5. Reconnect USB
6. Try again with different firmware variant

### If Write Success:
1. ✅ Wait for radio to restart completely
2. ✅ Radio should boot normally
3. ✅ Check all basic functions work
4. ✅ Navigate to K38 channel (27.385 MHz)
5. ✅ **Connect 50Ω dummy load** (CRITICAL!)
6. ✅ Select USB mode
7. ✅ Press PTT button
8. ✅ Verify NO "DISABLE" message
9. ✅ Verify TX LED lights up
10. ✅ Measure RF output (if spectrum analyzer available)

---

## 🎯 Success Criteria

**Firmware flash is successful if:**
- [ ] "Write Success" message appears
- [ ] Radio restarts automatically
- [ ] Radio powers on normally
- [ ] All channels accessible
- [ ] K38 channel present
- [ ] USB mode selectable
- [ ] PTT works without "DISABLE"
- [ ] TX LED activates
- [ ] RF output measurable

**PROJECT SUCCESS!** 🎉🎊🚀

---

## 📞 Next Steps After Success

1. **Document** which firmware variant worked
2. **Test** USB TX mode thoroughly
3. **Verify** no unintended side effects
4. **Backup** the working firmware
5. **Update** project documentation
6. **Share** results (if appropriate)
7. **Celebrate!** 🎉

---

## 🆘 If All Tests Fail

If all variants fail in both rounds:

1. **Capture USB traffic** with Wireshark + USBPcap
2. **Compare** successful flash (original firmware) vs failed flash (patched)
3. **Analyze** bootloader protocol responses
4. **Post** results for deeper analysis
5. **Consider** alternative approaches:
   - Direct memory patching
   - JTAG/SWD programming
   - Bootloader replacement
   - Different radio model

---

**Start testing now!** Good luck! 🍀
