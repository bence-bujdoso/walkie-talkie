# AM Mode Testing Guide - WILL WORK!

## Quick Start

### File to Load
```
TK11_K38_MODE_01_20251029_150652.dat
```

This file has K38 channel set to **AM mode (0x01)**, which IS allowed by firmware!

---

## Step-by-Step Testing

### 1. Load File in TK11.exe
- Open TK11.exe
- File → Open → `TK11_K38_MODE_01_20251029_150652.dat`
- You should see K38 channel named: **"K38 DSB 0x01"**
- Frequency: **2.7385 MHz**

### 2. Upload to Radio
- Connect radio via programming cable
- Upload configuration to radio
- Wait for completion

### 3. Select K38 Channel
- On radio, navigate to K38 channel
- Verify frequency shows: **2.7385 MHz**
- Channel name: **"K38 DSB 0x01"** or similar

### 4. Connect Dummy Load
⚠️ **IMPORTANT:** Use 50Ω dummy load, NOT antenna!

### 5. Press PTT
✅ **Expected:** PTT works! NO "DISABLE" message!
- TX LED should light up
- No blocking message

### 6. Monitor on Spectrum Analyzer
**Settings:**
- Center: 2.7385 MHz
- Span: 20-50 kHz
- RBW: 1-3 kHz

**What you should see (AM modulation):**
```
       /\
      /  \
   /\ |  | /\
  /  \|  |/  \
 ─────┴──┴─────
  LSB  C  USB

Carrier in center
Two symmetrical sidebands (LSB + USB)
```

This is AM modulation:
- Carrier power: ~50% of total
- LSB + USB contain audio

---

## Comparison Test

### Test Both Files

1. **FM Mode (baseline):**
   - File: `TK11_K38_MODE_00_20251029_150652.dat`
   - Should show single carrier with frequency deviation
   - PTT works (FM is allowed)

2. **AM Mode (test):**
   - File: `TK11_K38_MODE_01_20251029_150652.dat`
   - Should show carrier + 2 sidebands
   - PTT works (AM is allowed)

3. **DSB Mode 0x05 (blocked):**
   - File: `TK11_K38_MODE_05_20251029_150652.dat`
   - Shows "DISABLE" when PTT pressed
   - Firmware blocks transmission

---

## Questions to Answer

After testing AM mode:

1. ✅ Does PTT work without "DISABLE" message?
2. ✅ Does TX LED light up?
3. ✅ Can you see modulation on spectrum analyzer?
4. ✅ Does it look like AM (carrier + 2 sidebands)?

If YES to all → **AM mode works!**

Now the question is: **Is AM good enough, or do you need true DSB?**

---

## AM vs DSB - What's the Difference?

### AM (Amplitude Modulation)
```
Carrier:     50-70% of power
LSB sideband: 15-25% of power
USB sideband: 15-25% of power
Both sidebands contain same audio
```

### DSB-SC (Double Sideband Suppressed Carrier)
```
Carrier:     0-10% of power (suppressed!)
LSB sideband: 45-50% of power
USB sideband: 45-50% of power
Both sidebands contain same audio
```

**Key Difference:** DSB suppresses the carrier to put more power into sidebands.

**For CB Radio:** AM is standard and legal. DSB-SC is rare on CB.

---

## Next Steps Based on Results

### If AM Works and Looks Good
→ **Use AM mode for 11m band**
- It's legal for CB radio
- It's similar enough to DSB
- No firmware modification needed

### If You MUST Have True DSB
→ **Firmware patching required** (risky!)
- Patch TX validation mask
- But even then, hardware may not support DSB
- See: `DISABLE_FIX_ANALYSIS.md`

---

## Original K38 USB Test

Also test the **original TK11.dat** file:
- Load original file
- Select K38 USB channel
- Press PTT
- **Question:** Does it also show "DISABLE"?

If YES → K38 was always an RX-only channel
If NO → Something else is going on

---

**ACTION:** Test `TK11_K38_MODE_01_*.dat` NOW and report results!
