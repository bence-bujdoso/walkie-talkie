# Next Steps: Getting Test Write to Execute

## 🎯 Current Situation

**What works:**
- ✅ Engineering mode password (`tk11` or `unlock`)
- ✅ `main.gEngineerMode` gets set to `true`
- ✅ "Hide Param" tab appears

**What doesn't work:**
- ❌ Test write code doesn't execute automatically
- ❌ No diagnostic messages shown

## 🔍 Most Likely Cause

**The COM port is probably not open when Eng Mode button is clicked.**

The `ComPort.Instance.Open()` call is likely returning `false`, but there's no error message to tell you this.

### Why This Happens:

1. User clicks Eng Mode button
2. Password dialog appears
3. User enters password
4. Engineering mode activates
5. Code tries to open COM port
6. **Radio not connected yet** → Open() fails → Code stops

---

## ✅ Solution 1: Use DEBUG Version (RECOMMENDED)

**This will show exactly what's happening.**

### Steps:

1. **Open TK11.exe in dnSpy**

2. **Find `toolStripButton4_Click` method:**
   - Navigate to: `K7` → `main` class
   - Find: `toolStripButton4_Click` method (around line 765)

3. **Replace entire method with code from:**
   - `toolStripButton4_Click_DEBUG.cs`

4. **Save in dnSpy:**
   - Right-click `TK11.exe` in Assembly Explorer
   - Select "Save Module"
   - Save as `TK11_debug.exe`

5. **Test procedure:**
   ```
   a. Connect radio via USB
   b. Run TK11_debug.exe
   c. Click "Read" button (verify connection works)
   d. Click "Eng Mode" button
   e. Enter password: tk11
   f. Watch for DEBUG messages (A, B, C, D, E, F, G, etc.)
   g. Report which message appears LAST
   ```

### What DEBUG messages mean:

- **DEBUG A-F appear** → Code is running, approaching COM port
- **DEBUG G shows "returned: false"** → COM port not open (EXPECTED)
- **DEBUG G shows "returned: true"** → COM port opened! Write is executing
- **DEBUG J shows result** → Write completed, check return value

---

## ✅ Solution 2: Hook Into Channel Download (EASIEST)

**Add write code to an operation that ALREADY works.**

### Why this works:
- Channel download ALREADY opens COM port
- You've confirmed channel download works
- COM port guaranteed to be open
- Radio guaranteed to be connected

### Steps:

1. **Find channel download function in dnSpy:**
   - Look for function that writes channels TO radio
   - Probably in `wfm_progress` class
   - Look for button click event that downloads/writes channels

2. **Add test write at end:**
   - See code in `ALTERNATIVE_WRITE_DURING_CHANNEL_DOWNLOAD.cs`
   - Add AFTER channel data is written
   - BEFORE COM port is closed

3. **Usage:**
   ```
   a. Connect radio
   b. Enter Engineering mode (password: tk11)
   c. Click "Download" or "Write to Radio" button
   d. Channels will download normally
   e. THEN test write executes
   f. Message box shows result
   ```

---

## ✅ Solution 3: Manual Test Function

**Create a button that you click AFTER connecting radio.**

### Add this to any existing button in Engineering mode:

```csharp
private void TestWriteButton_Click(object sender, EventArgs e)
{
    try
    {
        // Check if radio connected
        if (!ComPort.Instance.IsOpen())
        {
            MessageBox.Show(
                "⚠️ Radio not connected!\n\n" +
                "Please:\n" +
                "1. Connect radio via USB\n" +
                "2. Click 'Read' button\n" +
                "3. Then try this again",
                "Not Connected"
            );
            return;
        }

        // Confirm before writing
        DialogResult result = MessageBox.Show(
            "Write 0x17 to config address 0x314D?\n\n" +
            "This will attempt to enable USB TX mode.",
            "Confirm Write",
            MessageBoxButtons.YesNo
        );

        if (result != DialogResult.Yes)
        {
            return;
        }

        // Perform write
        byte[] testValue = new byte[] { 0x17 };
        bool success = protocol_struct.Write(0x314D, testValue, 1);

        if (success)
        {
            MessageBox.Show(
                "✅ WRITE SUCCESSFUL!\n\n" +
                "Wrote 0x17 to config address 0x314D\n\n" +
                "Next steps:\n" +
                "1. Restart radio\n" +
                "2. Select K38 USB channel\n" +
                "3. Press PTT\n" +
                "4. Check if 'DISABLE' still appears\n\n" +
                "If still disabled: firmware reads from\n" +
                "flash (not config), need different approach.",
                "Success"
            );
        }
        else
        {
            MessageBox.Show(
                "❌ WRITE FAILED\n\n" +
                "protocol_struct.Write() returned false\n\n" +
                "Radio rejected the write command.\n" +
                "May need to try during channel operation.",
                "Failed"
            );
        }
    }
    catch (Exception ex)
    {
        MessageBox.Show(
            $"Exception:\n\n{ex.Message}\n\n{ex.StackTrace}",
            "Error"
        );
    }
}
```

---

## 🎯 Recommended Approach

**Try in this order:**

### 1️⃣ DEBUG Version (5 minutes)
- Quick to test
- Shows exactly what's failing
- Identifies root cause

### 2️⃣ Channel Download Hook (10 minutes)
- If DEBUG shows COM port issue
- Piggyback on working operation
- Most reliable approach

### 3️⃣ Manual Button (15 minutes)
- If you want full control
- User clicks when ready
- Can reuse multiple times

---

## 📊 What To Report Back

After trying DEBUG version, tell me:

1. **Which DEBUG message appeared LAST?**
   - Example: "Last message was DEBUG G: returned false"

2. **What did DEBUG G say exactly?**
   - This shows if COM port opened

3. **Any error messages?**
   - Full text of any MessageBox

4. **When did you click Eng Mode button?**
   - Before connecting radio?
   - After clicking "Read"?
   - After downloading channels?

---

## 🔍 Understanding the Results

### If COM port opens (DEBUG G: true):

**Write returns TRUE:**
- ✅ Config memory write succeeded
- Test USB TX on K38 channel
- If still disabled → Need to write to firmware flash

**Write returns FALSE:**
- ⚠️ Radio rejected write
- May need specific mode
- Try during channel download

### If COM port fails (DEBUG G: false):

**Solution:**
1. Connect radio FIRST
2. Click "Read" button
3. THEN click Eng Mode button
4. Or use Channel Download hook approach

---

## 🎯 Quick Test Checklist

**Correct procedure:**
- [ ] Connect TK11 radio via USB
- [ ] Run TK11.exe
- [ ] Click "Read" button → should show channel data
- [ ] Verify radio is connected (status indicator)
- [ ] THEN click "Eng Mode" button
- [ ] Enter password: `tk11`
- [ ] Watch for DEBUG messages

**Wrong procedure (will fail):**
- ❌ Run TK11.exe
- ❌ Click Eng Mode immediately
- ❌ Enter password
- ❌ COM port not open → Write fails silently

---

## 📁 Files Reference

- `toolStripButton4_Click_DEBUG.cs` - DEBUG version with 13 checkpoints
- `DEBUG_TEST_WRITE_NOT_EXECUTING.md` - Full debugging guide
- `ALTERNATIVE_WRITE_DURING_CHANNEL_DOWNLOAD.cs` - Hook into channel download
- `DIRECT_FLASH_WRITE_OPTIONS.md` - If config write doesn't work

---

## 🚨 Important

**If write succeeds BUT USB still shows DISABLE:**

This means firmware code reads TX mode from **firmware flash** (address 0x314D), not config memory (address 0x8314D).

**Next step:**
- Create `WriteFlashDirect()` function
- Write to flash address 0x314D (no 0x80000 offset)
- See: `DIRECT_FLASH_WRITE_OPTIONS.md`

---

**Start with DEBUG version and report the last DEBUG message you see!** 📊
