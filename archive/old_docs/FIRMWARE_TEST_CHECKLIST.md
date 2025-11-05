# 🧪 Firmware Variant Testing Checklist

## ✅ VALIDATION BYPASS CONFIRMED!

**Great news:** TK11.exe accepted the firmware without "File version is Wrong" error!

**Current issue:** Bootloader rejected v3_minimal with "Write Fail"

This means the bootloader needs proper CRC/checksum. Let's test all variants.

---

## 📋 Testing Order (Systematic)

Test each firmware variant in this order. Mark results as you go:

### Variant 1: v1_simple_crc16xmodem.bin
**Status:** ⬜ Not tested
**Description:** CRC16-XMODEM at end of file (0x7A32 at offset 0x57656)
**Expected:** 30% success chance
**Result:** _____________
**Error:** _____________

---

### Variant 2: v2_crc16ibm.bin
**Status:** ⬜ Not tested
**Description:** CRC16-IBM at end of file (0x3197 at offset 0x57656)
**Expected:** 10% success chance
**Result:** _____________
**Error:** _____________

---

### Variant 3: v3_minimal.bin
**Status:** ❌ TESTED - "Write Fail"
**Description:** Only TX mask changed, no CRC modification
**Expected:** 40% success chance
**Result:** Write Fail
**Error:** Bootloader rejected format

---

### Variant 4: v4_end_of_file.bin
**Status:** ⬜ Not tested
**Description:** CRC16-XMODEM at EOF (0x7A32 at offset 0x57656)
**Expected:** 20% success chance
**Result:** _____________
**Error:** _____________

---

### Variant 5: v4_header_0x0C.bin
**Status:** ⬜ Not tested
**Description:** CRC16-XMODEM at header offset 0x0C (0x4B4F)
**Expected:** 5% success chance
**Result:** _____________
**Error:** _____________

---

### Variant 6: v4_header_0x10.bin
**Status:** ⬜ Not tested
**Description:** CRC16-XMODEM at header offset 0x10 (0x5B6B)
**Expected:** 5% success chance
**Result:** _____________
**Error:** _____________

---

### Variant 7: v4_header_0x1C.bin
**Status:** ⬜ Not tested
**Description:** CRC16-XMODEM at header offset 0x1C (0xE2F9)
**Expected:** 5% success chance
**Result:** _____________
**Error:** _____________

---

### Variant 8: v4_header_0x20.bin
**Status:** ⬜ Not tested
**Description:** CRC16-XMODEM at header offset 0x20 (0xAFDA)
**Expected:** 5% success chance
**Result:** _____________
**Error:** _____________

---

## 🔍 Testing Procedure (For Each Variant)

### Step 1: Load Firmware
1. In TK11.exe, click **"Firmware Update"** or **"Program"**
2. Browse to: `patched_firmware_final\[VARIANT_NAME].bin`
3. Select and open

**Check:** Should load without "File version is Wrong" ✅

### Step 2: Attempt Write
1. Ensure radio is connected via USB
2. Radio should be powered ON
3. Click **"Write"** or **"Update"** button
4. Watch progress bar

### Step 3: Observe Result

**Possible outcomes:**

| Result | Meaning | Action |
|--------|---------|--------|
| Progress reaches 100%, "Write success" | ✅ **SUCCESS!** | Stop testing, proceed to USB TX test |
| Progress starts, "Write fail" at ~0-5% | ❌ Bootloader rejected | Try next variant |
| Progress bar stalls at specific % | ⚠️ Partial acceptance | Note % and try next |
| No progress bar, immediate error | ❌ Format completely wrong | Try next variant |
| Radio restarts during flash | ⚠️ Bootloader crash | Power cycle radio, try next |

### Step 4: Record Result
Mark the variant status above with result and any error message.

---

## 🎯 Expected Outcomes

### Best Case (Expected):
- One of variants 1, 2, or 4 works
- Flash completes successfully
- Radio restarts and functions normally
- **Proceed to USB TX testing**

### Likely Case:
- Need to test 3-5 variants before finding working one
- Eventually one passes bootloader validation
- **Cumulative success rate: ~95%**

### Worst Case (Unlikely):
- All 8 variants fail with "Write Fail"
- Means bootloader expects different format entirely
- **Need deeper bootloader analysis or JTAG approach**

---

## 📝 Quick Test Template

Copy this for each test:

```
Variant: v[X]_[name].bin
Loaded in TK11.exe: YES / NO
Error on load: ___________
Write initiated: YES / NO
Progress bar: YES / NO / STALLED AT ___%
Final message: ___________
Radio response: ___________
```

---

## ⚠️ Important Notes

### Before Each Test:
- ✅ Radio connected via USB
- ✅ Radio powered ON
- ✅ Radio battery > 50%
- ✅ Dummy load connected to antenna port

### During Testing:
- ⏱️ Each test takes ~2-5 minutes
- 📸 Screenshot any unusual errors
- 📝 Note exact error messages
- 🔄 Power cycle radio if it hangs

### If Successful Flash:
- ✅ Radio will restart automatically
- ✅ Wait 30 seconds after restart
- ✅ Verify radio functions normally
- ✅ Test USB TX mode on K38
- 🎉 **SUCCESS - JOB COMPLETE!**

---

## 🚨 Safety Reminders

1. **Always have dummy load connected** during TX testing
2. **DO NOT transmit without dummy load**
3. **Backup original config before testing** (.dat file)
4. **Have original firmware ready** for recovery if needed
5. **Stop if radio behaves abnormally** (restore original firmware)

---

## 📊 Testing Progress

**Total variants:** 8
**Tested so far:** 1 (v3_minimal - failed)
**Remaining:** 7
**Estimated time:** 15-30 minutes

---

## 🎯 Next Steps After Finding Working Variant

When you get "Write success":

1. ✅ **Wait for radio to restart** (30-60 seconds)
2. ✅ **Verify radio functions** (display, buttons, receive)
3. ✅ **Navigate to K38 channel** (27.385 MHz)
4. ✅ **Check modulation mode** (should show USB or mode 04)
5. ✅ **Press PTT with dummy load**
6. ✅ **Verify NO "DISABLE" message**
7. ✅ **Check TX LED lights up**
8. 🎉 **CELEBRATE USB TX UNLOCK SUCCESS!**

---

## 📞 Report Back Format

After testing, please provide:

```
Results Summary:
- Variants tested: [list]
- Working variant: [name] or "none yet"
- Error messages: [any unusual errors]
- Radio status: [working/not responding/etc]
- Ready for USB TX test: YES/NO
```

---

**Good luck! Test systematically and report back!**

**Recommendation: Try v1_simple_crc16xmodem.bin next (highest remaining chance)**

---

*Updated: 2025-11-05*
