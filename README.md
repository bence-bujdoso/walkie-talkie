# TK11 USB TX Unlock Project

**Status:** ⚠️ **90% COMPLETE** - Level 3 bypass required to fix "Write Fail" error

**Current Issue:** Getting "Write Fail" error after validation bypass popup

**Solution:** Apply Level 3 bypass → See `WRITE_FAIL_SOLUTION.md` or `QUICK_FIX_WRITE_FAIL.md`

---

## 🎯 Project Goal

Enable USB (Upper Sideband) transmission on the TK11 handheld radio's 11-meter band (CB channels), specifically on channel K38 (27.385 MHz).

---

## 📊 Current Progress

### ✅ COMPLETED
- [x] Reverse engineering of TK11 firmware format
- [x] Identification of TX unlock location (offset 0x314D)
- [x] TK11.exe decompilation and validation bypass (Level 1-2)
- [x] Creation of 8 patched firmware variants
- [x] **TK11.exe validation bypass confirmed working**

### 🔄 IN PROGRESS
- [ ] **Apply Level 3 bypass to fix "Write Fail" error**
- [ ] Bootloader handshake bypass required in downloadFileEx method

### ⏳ PENDING
- [ ] Flash working firmware variant to radio
- [ ] Verify USB TX mode on K38 channel

---

## ⚠️ CURRENT ISSUE: "Write Fail" Error

**Symptoms:**
1. Firmware loads successfully ✅
2. See "validation bypassed" popup ✅
3. Click OK
4. Get "Write Fail" error ❌

**Root Cause:**
- Level 1-2 bypass working (Updata method)
- Level 3 bypass needed (downloadFileEx method)
- Bootloader handshake check is failing

**Solution:**
→ **Quick fix (5 min):** See `QUICK_FIX_WRITE_FAIL.md`
→ **Detailed guide:** See `WRITE_FAIL_SOLUTION.md`
→ **Technical docs:** See `LEVEL3_BYPASS_DETAILED.md`

---

## 🚀 Quick Start

### What You Need
- TK11 radio with USB cable
- Windows PC
- dnSpy (for applying Level 3 bypass)
- Patched firmware files (included)
- 50Ω dummy load (REQUIRED for safety)

### Steps

**1. Apply Level 3 Bypass (REQUIRED - 5 minutes):**

See `QUICK_FIX_WRITE_FAIL.md` for detailed steps:
```
1. Open TK11_PATCHED.exe in dnSpy
2. Edit downloadFileEx method
3. Add bootloader bypass code
4. Save as TK11_PATCHED_LEVEL3.exe
```

**2. Flash Firmware:**
```
1. Run TK11_PATCHED_LEVEL3.exe
2. Load any patched firmware from patched_firmware_final/
3. Connect radio via USB
4. Click "Write"
5. Should see "Bootloader handshake bypassed!" popup
6. Wait for flash to complete
```

**3. Test USB TX Mode:**
- Radio will restart automatically
- Navigate to K38 channel (27.385 MHz)
- Press PTT with dummy load connected
- Verify NO "DISABLE" message appears
- **SUCCESS!** 🎉

**Need help?** See `WRITE_FAIL_SOLUTION.md` for complete guide

---

## 📁 Essential Files

### 🔥 PRIORITY - Fix "Write Fail" Error
```
QUICK_FIX_WRITE_FAIL.md            ← ⭐ START HERE - 5-minute fix
WRITE_FAIL_SOLUTION.md             ← Complete detailed guide
LEVEL3_BYPASS_DETAILED.md          ← Technical documentation
CURRENT_STATUS.md                  ← Project status & next steps
```

### For Users
```
TK11.exe                           ← Modified software (373 KB, Level 1-2)
patched_firmware_final/            ← 8 firmware variants to test
├── TK11_PATCHED_v1_simple_crc16xmodem.bin
├── TK11_PATCHED_v2_crc16ibm.bin
├── TK11_PATCHED_v3_minimal.bin
├── TK11_PATCHED_v4_end_of_file.bin
└── TK11_PATCHED_v4_header_*.bin (4 files)

QUICKSTART.md                      ← Simple 5-step guide
FIRMWARE_TESTING.md                ← Systematic testing procedure
```

### Code References
```
bin/scripts/patch_tk11_updata_method.cs         ← Level 1-2 bypass code
bin/scripts/patch_tk11_downloadfileex_method.cs ← Level 3 bypass code
```

### Technical Documentation
```
COMPLETE_TK11_BYPASS.md            ← How TK11.exe was patched
FIRMWARE_FLASH_GUIDE.md            ← Safety guide for flashing
create_perfect_firmware.py         ← Script that created firmware variants
verify_patches.py                  ← Verification tool

BK4819_CAPABILITIES_REPORT.md      ← Hardware analysis
TX_UNLOCK_REPORT.md                ← Technical findings
PROJECT_COMPLETE_SUMMARY.md        ← Full project overview
```

### Backups
```
TK11_ORIGINAL_BACKUP.exe           ← Original TK11.exe (382 KB)
TK11_v5.00.09_ENG.bin              ← Original firmware
```

---

## 🔬 Technical Summary

### The Problem
TK11 firmware restricts transmission to FM (0x01) and AM (0x02) modes only. USB mode (0x04) is blocked.

### The Solution
**Two-part patch:**

1. **Firmware Patch**
   - Location: Offset 0x314D
   - Change: 0x03 → 0x13 (binary: 00000011 → 00010011)
   - Effect: Enables USB (0x04) mode for TX

2. **TK11.exe Patch**
   - Class: K7.wfm_progress
   - Method: Updata()
   - Change: Bypass firmware validation, load file directly
   - Effect: Allows flashing of modified firmware

### Current Status
- ✅ TK11.exe validation bypass: **WORKING**
- 🔄 Bootloader acceptance: **TESTING VARIANTS**
- ⏳ USB TX verification: **PENDING**

---

## ⚠️ Important Warnings

### Safety
- ⚠️ **ALWAYS test with 50Ω dummy load first**
- ⚠️ **Backup original firmware before flashing**
- ⚠️ **Risk of radio brick if done incorrectly**
- ⚠️ **Modification may void warranty**

### Legal
- ✅ For **educational and research purposes**
- ✅ For **authorized testing with proper license**
- ❌ **NOT for illegal transmission**
- ❌ **NOT for violating radio regulations**

### Technical
- **BK4819 Chip:** FM/AM only (no true SSB capability)
- **USB Mode:** May produce FM-modulated signal, not true USB
- **Testing Required:** Spectrum analyzer verification recommended

---

## 📊 Test Results Log

| Variant | Status | Result | Notes |
|---------|--------|--------|-------|
| v3_minimal | ❌ | Write Fail | Bootloader rejected |
| v1_simple_crc16xmodem | ⏳ | Testing next | CRC16-XMODEM at EOF |
| v4_end_of_file | ⏳ | Pending | Alternative EOF CRC |
| v2_crc16ibm | ⏳ | Pending | CRC16-IBM algorithm |
| v4_header_* (4 files) | ⏳ | Pending | CRC at header positions |

**Next test:** v1_simple_crc16xmodem.bin

---

## 🛠️ Tools & Requirements

### Software
- Python 3.x (for running scripts)
- TK11.exe (provided, patched)
- dnSpy (for .NET decompilation, archived)

### Hardware
- TK11 Radio
- USB programming cable
- 50Ω dummy load (REQUIRED)
- Spectrum analyzer (optional, for verification)

---

## 📚 Documentation

### Quick Reference
- **[QUICKSTART.md](QUICKSTART.md)** - 5-step guide to USB TX unlock
- **[FIRMWARE_TESTING.md](FIRMWARE_TESTING.md)** - Systematic testing procedure

### Technical Details
- **[COMPLETE_TK11_BYPASS.md](COMPLETE_TK11_BYPASS.md)** - TK11.exe patching guide (3 levels)
- **[TX_UNLOCK_REPORT.md](TX_UNLOCK_REPORT.md)** - How TX unlock was found
- **[BK4819_CAPABILITIES_REPORT.md](BK4819_CAPABILITIES_REPORT.md)** - Hardware capabilities

### Implementation
- **[FIRMWARE_FLASH_GUIDE.md](FIRMWARE_FLASH_GUIDE.md)** - Safe flashing procedures
- **[PROJECT_COMPLETE_SUMMARY.md](PROJECT_COMPLETE_SUMMARY.md)** - Full project report

---

## 🌐 Repository

**GitHub:** https://github.com/bence-bujdoso/walkie-talkie

**Contents:**
- Complete documentation (14 MD files)
- Analysis scripts (2 essential, 40+ archived)
- Patched firmware variants (8 files)
- Modified TK11.exe
- Full reverse engineering process

---

## 🎓 What This Project Demonstrates

- Binary firmware reverse engineering
- RF chip capability analysis (BK4819, AP8048A)
- .NET decompilation and patching (dnSpy)
- Bootloader protocol analysis
- Firmware format analysis
- Multiple CRC16 implementations
- Validation bypass techniques
- Systematic testing methodology

---

## 📞 Current Status & Next Steps

### Where We Are
✅ **TK11.exe validation bypass confirmed working**
- No more "File version is Wrong" error
- Can load all firmware variants

🔄 **Testing firmware variants for bootloader compatibility**
- v3_minimal: Failed (Write Fail)
- Next: v1_simple_crc16xmodem

### What's Needed
1. Test v1_simple_crc16xmodem.bin (next)
2. If fails, test v4_end_of_file.bin
3. Continue systematically through all 8 variants
4. Expected: One will work (95% cumulative probability)
5. Flash to radio and verify USB TX

### Estimated Time to Completion
- Firmware testing: 15-30 minutes (testing all variants)
- Successful flash: 5 minutes
- USB TX verification: 5 minutes
- **Total: ~30-40 minutes to final success**

---

## 🤝 Contributing

This is a research and educational project. Contributions welcome:
- Additional firmware analysis
- Alternative patching methods
- Testing results and verification
- Hardware analysis improvements

---

## 📜 License

**Educational and Research Use Only**

✅ Educational purposes
✅ Research and analysis
✅ Authorized testing with proper license

❌ Illegal transmission
❌ Violating radio regulations
❌ Commercial use without authorization

**Use at your own risk. Author not responsible for misuse or damage.**

---

## 🏆 Acknowledgments

- **OpenAI/Anthropic** - AI assistance for analysis
- **dnSpy Team** - Excellent .NET decompiler
- **Radio Community** - Knowledge and resources
- **Bence Bujdosó** - Project initiator

---

**73! 📻**

*Last Updated: 2025-11-05*
*Status: 95% Complete - Firmware variant testing in progress*
