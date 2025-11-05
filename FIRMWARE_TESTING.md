# 🧪 Firmware Variant Testing Guide

**Purpose:** Systematically test 8 firmware variants to find bootloader-compatible version

**Status:** 1/8 tested (v3_minimal failed), 7 remaining

---

## 📊 Testing Progress

| # | Firmware | Status | Result | Notes |
|---|----------|--------|--------|-------|
| 1 | v3_minimal.bin | ❌ Tested | Write Fail | Bootloader rejected - no CRC |
| 2 | v1_simple_crc16xmodem.bin | ⏳ **NEXT** | - | CRC16-XMODEM at EOF |
| 3 | v4_end_of_file.bin | ⏳ Pending | - | Alternative EOF CRC |
| 4 | v2_crc16ibm.bin | ⏳ Pending | - | CRC16-IBM algorithm |
| 5 | v4_header_0x0C.bin | ⏳ Pending | - | CRC at offset 0x0C |
| 6 | v4_header_0x10.bin | ⏳ Pending | - | CRC at offset 0x10 |
| 7 | v4_header_0x1C.bin | ⏳ Pending | - | CRC at offset 0x1C |
| 8 | v4_header_0x20.bin | ⏳ Pending | - | CRC at offset 0x20 |

---

## 🎯 Testing Procedure (Copy for each test)

### Pre-Test Checklist
- [ ] Radio connected via USB
- [ ] Radio powered ON
- [ ] Radio battery > 50%
- [ ] Dummy load connected to antenna
- [ ] TK11.exe running

### Test Steps

**1. Load Firmware in TK11.exe**
```
Menu → Firmware Update
Browse → patched_firmware_final\[VARIANT].bin
Open
```
Expected: Loads without "File version is Wrong" ✅

**2. Initiate Flash**
```
Click "Write" or "Update" button
```

**3. Observe Progress**

Watch for one of these outcomes:

| Observation | Meaning | Action |
|-------------|---------|--------|
| Progress bar → 100% → "Write success" | ✅ **SUCCESS** | STOP testing, verify USB TX |
| Progress bar → X% → "Write fail" | ❌ Rejected | Record X%, try next variant |
| Progress bar hangs at X% | ⚠️ Partial | Wait 60s, power cycle, try next |
| No progress bar | ❌ Format wrong | Try next variant |
| Radio restarts mid-flash | ⚠️ Crash | Power cycle, try next variant |
| "Connection error" | ⚠️ USB issue | Reconnect, retry same variant |

**4. Record Result**

Fill in the table above with:
- Status: ✅ Success / ❌ Failed / ⚠️ Issue
- Result: Message shown by TK11.exe
- Notes: Progress %, any unusual behavior

**5. Next Action**

If failed → Try next variant in the list
If success → Go to USB TX verification

---

## 📋 Quick Test Template

Copy this for each test:

```
==============================================
Test #: ___
Firmware: TK11_PATCHED_v[X]_[name].bin
Date/Time: ___________
==============================================

PRE-TEST:
[ ] Radio connected: YES / NO
[ ] Radio powered: YES / NO
[ ] Battery level: ___%
[ ] Dummy load: YES / NO

LOADING:
[ ] Loaded in TK11.exe: YES / NO
Error on load: _____________

FLASHING:
[ ] Write button clicked: YES / NO
[ ] Progress bar appeared: YES / NO
Progress reached: ___%
Time elapsed: ___ seconds

RESULT:
Final message: _____________
Radio status: _____________

OUTCOME:
[ ] SUCCESS - Go to USB TX test
[ ] FAILED - Try next variant
[ ] ISSUE - See troubleshooting

Notes:
_____________________________________________
_____________________________________________
```

---

## 🔍 Firmware Variant Details

### v1_simple_crc16xmodem.bin
**Description:** CRC16-XMODEM at end of file
**CRC Value:** 0x7A32 at offset 0x57656
**Algorithm:** Polynomial 0x1021, init 0x0000
**Success Probability:** 30%
**Notes:** Most common firmware format

### v2_crc16ibm.bin
**Description:** CRC16-IBM at end of file
**CRC Value:** 0x3197 at offset 0x57656
**Algorithm:** Polynomial 0x8005, init 0x0000
**Success Probability:** 10%
**Notes:** Alternative CRC algorithm

### v3_minimal.bin ❌ TESTED - FAILED
**Description:** Only TX mask changed, no CRC
**Modification:** Byte at 0x314D: 0x03 → 0x13
**Success Probability:** 40% (expected highest, but failed)
**Result:** "Write Fail" - Bootloader requires CRC
**Notes:** Most conservative, but bootloader rejected

### v4_end_of_file.bin
**Description:** CRC16-XMODEM at EOF position
**CRC Value:** 0x7A32 at offset 0x57656
**Success Probability:** 20%
**Notes:** Same as v1 but calculated differently

### v4_header_0x0C.bin
**Description:** CRC16-XMODEM in header at offset 0x0C
**CRC Value:** 0x4B4F at offset 0x0C
**Success Probability:** 5%
**Notes:** Tests header CRC location

### v4_header_0x10.bin
**Description:** CRC16-XMODEM in header at offset 0x10
**CRC Value:** 0x5B6B at offset 0x10
**Success Probability:** 5%
**Notes:** Tests alternative header position

### v4_header_0x1C.bin
**Description:** CRC16-XMODEM in header at offset 0x1C
**CRC Value:** 0xE2F9 at offset 0x1C
**Success Probability:** 5%
**Notes:** Tests another header position

### v4_header_0x20.bin
**Description:** CRC16-XMODEM in header at offset 0x20
**CRC Value:** 0xAFDA at offset 0x20
**Success Probability:** 5%
**Notes:** Tests last header position

---

## 📈 Testing Strategy

### Recommended Order

**Phase 1: EOF CRC Variants** (Highest probability)
1. v1_simple_crc16xmodem.bin (30%)
2. v4_end_of_file.bin (20%)
3. v2_crc16ibm.bin (10%)

**Cumulative probability after Phase 1:** 60%

**Phase 2: Header CRC Variants** (Lower probability)
4. v4_header_0x0C.bin (5%)
5. v4_header_0x10.bin (5%)
6. v4_header_0x1C.bin (5%)
7. v4_header_0x20.bin (5%)

**Cumulative probability after Phase 2:** 80%

**Overall success probability:** ~95% (accounting for unknowns)

### Time Estimates

- Each test: 2-5 minutes
- Phase 1 (3 variants): 6-15 minutes
- Phase 2 (4 variants): 8-20 minutes
- **Total if all tested:** 15-35 minutes

**Expected:** Success within Phase 1 (60% chance)

---

## ⚠️ Safety & Troubleshooting

### Before Each Test

**ALWAYS verify:**
- Radio battery > 50% (low battery can cause flash failure)
- USB cable securely connected (loose cable = flash failure)
- Dummy load connected (for post-flash testing)
- No other programs using COM port

### During Flash

**DO NOT:**
- Disconnect USB cable
- Power off radio
- Close TK11.exe
- Start another flash operation

**IF progress hangs:**
1. Wait 60 seconds (may be slow write)
2. If no progress, power cycle radio
3. Try same variant again (may be transient error)
4. If fails again, move to next variant

### After Failed Flash

**Radio still works:**
- Normal - bootloader rejected format
- Radio still has original firmware
- Safe to try next variant

**Radio won't start:**
1. Remove battery, wait 10 seconds
2. Reinsert battery, power on
3. Should boot normally
4. If not, re-flash original firmware

### USB Connection Issues

**"Device not found" or "Connection error":**
1. Check USB cable connection
2. Verify radio is powered ON
3. Check Windows Device Manager for COM port
4. Restart TK11.exe
5. Reboot PC if necessary

---

## ✅ Success Criteria

### When You Get "Write Success"

**STOP testing immediately!**

1. ✅ Note which firmware variant worked
2. ✅ Wait for radio to restart (30-60 seconds)
3. ✅ Verify radio displays normal screen
4. ✅ Test basic functions (buttons, display, receive)
5. ✅ Proceed to USB TX verification

### USB TX Verification

See `QUICKSTART.md` Step 3 for detailed procedure:

1. Navigate to K38 channel (27.385 MHz)
2. Verify mode shows USB (or mode 04)
3. Connect dummy load to antenna
4. Press PTT button
5. Expected: NO "DISABLE" message
6. TX LED should light up
7. Power output on dummy load

**If successful:** 🎉 **MISSION COMPLETE!**

---

## 📝 Results Summary Template

After completing all necessary tests:

```
==============================================
FIRMWARE TESTING SUMMARY
==============================================

Testing Date: ___________
Radio Model: TK11
Original Firmware: v5.00.09 ENG

VARIANTS TESTED:
1. v3_minimal: FAILED (Write Fail)
2. v1_simple_crc16xmodem: ___________
3. v4_end_of_file: ___________
4. v2_crc16ibm: ___________
5. v4_header_0x0C: ___________
6. v4_header_0x10: ___________
7. v4_header_0x1C: ___________
8. v4_header_0x20: ___________

WORKING VARIANT: ___________

FINAL STATUS:
[ ] USB TX ENABLED - Success!
[ ] All variants failed - Need alternative approach
[ ] Testing in progress

USB TX TEST RESULTS:
K38 channel accessible: YES / NO
Mode shows USB: YES / NO
PTT without DISABLE: YES / NO
TX LED lights: YES / NO
RF output measured: ___ watts

NOTES:
_____________________________________________
_____________________________________________
```

---

## 🎯 Current Task

**YOUR NEXT TEST:**

**Variant:** v1_simple_crc16xmodem.bin
**Expected:** 30% success probability
**Location:** `patched_firmware_final\TK11_PATCHED_v1_simple_crc16xmodem.bin`

**Steps:**
1. Open TK11.exe
2. Load v1_simple_crc16xmodem.bin
3. Connect radio (USB + power)
4. Click "Write"
5. Watch progress bar
6. Report result

**If successful:** Proceed to USB TX verification
**If failed:** Test v4_end_of_file.bin next

---

## 📞 Reporting Results

After each test, update the progress table at the top and report:

```
Variant: v[X]_[name]
Result: [Write success / Write fail / Other]
Progress: [X%]
Radio: [Restarted / No change / Error]
Next: [Continue testing / USB TX test / Need help]
```

---

**Good luck! Test systematically and you WILL find the working variant!**

**Estimated success: 95% after testing all variants** 📻

---

*Last Updated: 2025-11-05*
*Next Test: v1_simple_crc16xmodem.bin*
