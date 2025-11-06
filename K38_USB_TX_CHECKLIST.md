# K38 USB TX - Quick Checklist

**Issue**: "DISABLE" message still appears when trying to transmit on K38 USB

---

## ✅ Two-Part Solution Required

### Part 1: TK11.dat File (Channel Configuration)
```
Location: E:\AI\tk11\TK11.dat
Record: 0 (K38 USB channel)
Required bytes:
  - Offset 0x16 (byte 22): 0xFF (TX enabled)
  - Offset 0x17 (byte 23): 0x04 (USB mode)

Status: [ ] Complete
```

### Part 2: Firmware Patch (Permission System) ⚠️ CRITICAL
```
Location: Flash patched firmware to radio
Required change: Offset 0x314D: 0x03 → 0x13

Status: [ ] Complete

Steps:
1. [ ] Have original firmware (TK11_v5.00.09_ENG.bin)
2. [ ] Generate patched variants: python create_perfect_firmware.py
3. [ ] Patch TK11.exe with dnSpy (if not already done)
4. [ ] Flash TK11_PATCHED_v1_simple_crc16xmodem.bin to radio
5. [ ] Test: Press PTT on K38 - "DISABLE" should be gone
```

---

## 🔍 Quick Diagnostic

**Q: Does "DISABLE" message appear when pressing PTT on K38?**
- **YES** → Firmware NOT patched (Part 2 incomplete)
- **NO** → Success! USB TX is working

**Q: Do files exist in `E:\AI\tk11\patched_firmware_final\`?**
- **YES** → Good, proceed to flashing
- **NO** → Run `python create_perfect_firmware.py`

**Q: Is TK11.exe size ~373 KB (patched)?**
- **YES** → Good, can load modified firmware
- **NO (382 KB)** → Need to patch with dnSpy first

---

## 🎯 Most Likely Issue

**Root cause**: .dat file modified (Part 1) but firmware not flashed (Part 2)

**Why it doesn't work**:
- TK11.dat says "use USB mode" ✅
- Firmware says "USB mode not allowed" ❌
- Result: "DISABLE" message appears

**Solution**: Flash patched firmware (Part 2)

---

## 🚀 Quick Fix (15 minutes)

```bash
# Step 1: Generate firmware (if not already done)
cd E:\AI\tk11\
python create_perfect_firmware.py

# Step 2: Flash firmware
# - Open TK11.exe (patched version, ~373 KB)
# - Load: patched_firmware_final\TK11_PATCHED_v1_simple_crc16xmodem.bin
# - Connect radio
# - Click "Write"
# - Wait for success

# Step 3: Test
# - Radio restarts
# - Navigate to K38 channel
# - Press PTT with dummy load
# - "DISABLE" should NOT appear
# - TX LED should light up
```

---

## 📞 Report Back

After flashing firmware, report:
- [ ] Which firmware variant worked (v1, v2, v4, etc.)
- [ ] "DISABLE" message gone? (YES/NO)
- [ ] TX LED lights up? (YES/NO)
- [ ] Can transmit? (YES/NO)
- [ ] Any error messages?

---

## 📚 Detailed Instructions

See: **`K38_USB_TX_DIAGNOSTIC.md`** for complete diagnostic and solution guide

---
