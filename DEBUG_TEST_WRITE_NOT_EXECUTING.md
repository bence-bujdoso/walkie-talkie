# Debugging: Test Write Not Executing

## 🔍 Problem

After entering Engineering mode password successfully, the automatic test write code doesn't execute. User only sees "Success" message, then nothing happens.

## ✅ What Works

- Password validation succeeds
- `main.gEngineerMode` gets set to `true`
- "Hide Param" tab appears correctly

## ❌ What Doesn't Work

- The test write code block after "Hide Param" doesn't execute
- No error messages shown
- No indication of what's happening

---

## 🎯 Debugging Steps

### Step 1: Use the DEBUG Version

Replace your `toolStripButton4_Click` method with the version in `toolStripButton4_Click_DEBUG.cs`.

This version has **13 debug checkpoints** (DEBUG A through DEBUG M) that will show exactly where execution stops.

**What to look for:**

1. **If you see DEBUG A, B, C, D, E, F** → Code is executing
2. **If execution stops at DEBUG G** → COM port open is failing
3. **If you see all debugs but no "Success"** → Write is failing

### Step 2: Check COM Port State

**Before clicking Eng Mode button, check:**

1. Is radio connected via USB?
2. Is TK11.exe showing "Connected" status?
3. What COM port is selected in TK11 settings?

**Common COM port issues:**

- **Port already open**: If you just loaded/downloaded channels, port may still be open
- **Radio not connected**: Must connect radio BEFORE entering Eng Mode
- **Wrong port selected**: Check Settings → COM port number matches Device Manager

---

## 🔧 Alternative Approach 1: Separate Button

If automatic execution doesn't work, create a separate button for the write operation:

### Option A: Use existing Engineering Mode features

After entering Eng Mode, explore the GUI for:
- Memory read/write buttons
- Service commands
- Debug tools
- Direct access features

Look in:
- New menu items that appeared
- New tabs (besides "Hide Param")
- Buttons that became enabled

### Option B: Create new button in dnSpy

If no write functions exist in GUI, you can add a button:

1. Find a form with buttons (like `wfm_main`)
2. Copy an existing button
3. Modify its click event to call:
   ```csharp
   byte[] value = new byte[] { 0x17 };
   bool success = protocol_struct.Write(0x314D, value, 1);
   MessageBox.Show(success ? "Write Success!" : "Write Failed!");
   ```

---

## 🔧 Alternative Approach 2: Memory Scanner

Use the memory scanner to find and patch ALL occurrences of TX mask:

**Run the scanner:**
```csharp
// Add this to any button click event in Engineering mode
MemoryScanner.ScanForTXMask();
```

This will:
1. Scan config memory from 0x0 to 0x30000
2. Find all bytes with value 0x03
3. Show their addresses
4. Allow you to patch each one to 0x17

**Usage:**
```csharp
// After scanner finds addresses, patch them:
MemoryScanner.PatchAddress(0x314D, 0x17);   // Example
```

Code is in `memory_scanner_script.cs`.

---

## 🔧 Alternative Approach 3: Manual Write Function Call

If automatic execution fails, manually call the write function:

### Step 1: Find a button in Engineering mode

Look for any button you can repurpose in Eng mode (like a "Test" button or "Service" button).

### Step 2: Replace its click event

```csharp
private void someButton_Click(object sender, EventArgs e)
{
    try
    {
        if (!ComPort.Instance.IsOpen())
        {
            if (!ComPort.Instance.Open())
            {
                MessageBox.Show("Failed to open COM port!");
                return;
            }
        }

        byte[] value = new byte[] { 0x17 };
        bool success = protocol_struct.Write(0x314D, value, 1);

        if (success)
        {
            MessageBox.Show("Write Success! Test USB TX now.");
        }
        else
        {
            MessageBox.Show("Write Failed! Radio rejected write.");
        }
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}");
    }
}
```

---

## 🔧 Alternative Approach 4: Write During Channel Load/Save

Hook into existing channel operations:

### Option A: Modify channel download function

When downloading channels TO radio, add the write:

```csharp
// Find the function that downloads channels (probably in wfm_progress)
// Add this AFTER channels are written:

if (main.gEngineerMode)  // Only in Eng mode
{
    byte[] value = new byte[] { 0x17 };
    protocol_struct.Write(0x314D, value, 1);
}
```

### Option B: Modify channel upload function

When reading channels FROM radio, add the write:

```csharp
// After reading channels successfully:

if (main.gEngineerMode)
{
    byte[] value = new byte[] { 0x17 };
    protocol_struct.Write(0x314D, value, 1);
}
```

---

## 🎯 Expected Results After Successful Write

### If Write to Config Memory Works:

**Scenario A: Config memory controls TX**
- Write succeeds
- Radio restarts (or you restart it)
- K38 USB TX works
- No more "DISABLE" message

**Scenario B: Config memory doesn't control TX**
- Write succeeds (returns true)
- Radio accepts the write
- BUT K38 USB still shows "DISABLE"
- → Means firmware code reads from firmware flash, not config

---

## 🔍 Next Steps Based on Debug Results

### If DEBUG stops at "COM port failed to open":

**Solution**: Connect radio BEFORE entering Eng Mode
1. Connect radio
2. Click "Read" or "Connect" in TK11
3. Wait for successful connection
4. THEN click Eng Mode button

### If DEBUG shows "Write returned false":

**Solutions**:
1. Radio may require specific mode for config writes
2. Try writing during channel download operation
3. May need different message type (not 509)

### If DEBUG shows "Write returned true" but USB still disabled:

**Solution**: Need to write to firmware flash, not config memory
- Use approaches from `DIRECT_FLASH_WRITE_OPTIONS.md`
- Create `WriteFlashDirect()` function without 0x80000 offset
- Try different base addresses

---

## 📋 Checklist

**Before testing:**
- [ ] Radio connected via USB
- [ ] TK11 shows "Connected" status
- [ ] Correct COM port selected
- [ ] Engineering mode password works
- [ ] Debug version of code installed

**During testing:**
- [ ] Note which DEBUG message appears last
- [ ] Check if any error messages appear
- [ ] Verify COM port opens successfully
- [ ] Check Write() return value

**After testing:**
- [ ] Report which debug checkpoint failed
- [ ] Test USB TX on K38 channel
- [ ] Check if "DISABLE" still appears

---

## 🚨 Important Notes

### If Write Succeeds But USB Still Disabled

This means firmware code is checking firmware flash (address 0x314D), not config memory (address 0x8314D).

**Next steps:**
1. Create `WriteFlashDirect()` function (see `DIRECT_FLASH_WRITE_OPTIONS.md`)
2. Try writing to flash address 0x314D (without 0x80000 offset)
3. Or use different message type for flash writes

### Backup Before Writing

Before ANY write operation:
```csharp
// Read current value
byte[] backup = protocol_struct.Read(0x314D, 1);
// Save it somewhere - if radio bricks, you can restore
```

---

## 🎯 Quick Test Procedure

1. **Connect radio**
2. **Open TK11.exe**
3. **Click Read (verify connection)**
4. **Click Eng Mode button**
5. **Enter password** (`tk11` or `unlock`)
6. **Watch for DEBUG messages**
7. **Report results**

---

**Start with the DEBUG version and report which message appears last!**
