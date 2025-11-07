# Option: Create Direct Flash Write Function

## 🎯 If Config Memory Test Fails

If writing to config memory (0x314D) doesn't fix the USB TX issue, we need to write directly to **firmware flash** at address 0x314D (without the 0x80000 offset).

---

## 🔧 Option 1: Create New Function (RECOMMENDED)

**Add this new function to protocol_struct class:**

```csharp
// NEW FUNCTION: Direct flash write (no offset)
public static bool WriteFlashDirect(int address, byte[] data, ushort len)
{
    protocol_struct.MSG_CALMS_ParaWriteReq msg_CALMS_ParaWriteReq = default(protocol_struct.MSG_CALMS_ParaWriteReq);
    msg_CALMS_ParaWriteReq.struMsgHeader.u16MsgType = 509;
    msg_CALMS_ParaWriteReq.struMsgHeader.u16MsgLen = 12;

    // ⭐ NO OFFSET - Write directly to flash address
    msg_CALMS_ParaWriteReq.u32Address = (uint)address;  // Changed from (524288 + address)

    msg_CALMS_ParaWriteReq.u8DataLen = len;
    msg_CALMS_ParaWriteReq.u32MagicCode = protocol_struct.magiccode;
    byte[] array = Iparse.StructToBytes(msg_CALMS_ParaWriteReq, Iparse.GetStructSizeof(msg_CALMS_ParaWriteReq));
    byte[] array2 = new byte[array.Length + (int)len];
    Array.Copy(array, array2, array.Length);
    Array.Copy(data, 0, array2, array.Length, (int)len);

    if (ComPort.Instance.Write(protocol_struct.makefram(array2)))
    {
        array2 = ComPort.Instance.Read(1000);
        if (array2 != null)
        {
            array2 = protocol_struct.PareData(array2);
            if (array2 != null)
            {
                BitConverter.ToUInt16(array2, 0);
                return true;
            }
        }
    }
    return false;  // ⭐ Changed: return false on failure (original returns true)
}
```

**Then call it:**
```csharp
byte[] newValue = new byte[] { 0x17 };
bool success = protocol_struct.WriteFlashDirect(0x314D, newValue, 1);
```

**Advantages:**
- ✅ Keeps original Write() function intact
- ✅ Won't break anything else
- ✅ Safe to test

---

## 🔧 Option 2: Modify Existing Function (RISKY)

**Only do this if Option 1 doesn't work!**

Change this line in the existing Write() function:

**From:**
```csharp
msg_CALMS_ParaWriteReq.u32Address = (uint)(524288 + address);
```

**To:**
```csharp
// ⭐ Modified: Allow negative addresses to bypass offset
if (address < 0)
{
    // Negative address = direct flash write
    msg_CALMS_ParaWriteReq.u32Address = (uint)(-address);
}
else
{
    // Positive address = config memory (original behavior)
    msg_CALMS_ParaWriteReq.u32Address = (uint)(524288 + address);
}
```

**Then call it:**
```csharp
// Use negative address to signal "direct flash write"
byte[] newValue = new byte[] { 0x17 };
bool success = protocol_struct.Write(-0x314D, newValue, 1);  // Negative!
```

**Disadvantages:**
- ⚠️ Modifies existing function
- ⚠️ Could break other code
- ⚠️ Less clean

---

## 🔧 Option 3: Use Different Message Type

The current code uses message type `509` (O_CALMS_PARA_WRITE_REQ). There might be a different message type for flash writes.

**Check the MessageType enum for:**
- Flash write commands
- Firmware write commands
- Direct write commands

**Look for:**
```csharp
public enum MessageType
{
    // ... existing types ...
    O_CALMS_FLASH_WRITE_REQ = ???,
    O_CALMS_FIRMWARE_WRITE_REQ = ???,
    // etc.
}
```

If you find one, create a new function using that message type instead.

---

## 🎯 Recommended Approach

**Step 1:** Test config memory write first (use existing Write function)

**Step 2:** If that fails, try Option 1 (create WriteFlashDirect function)

**Step 3:** If that fails, try different flash base addresses:
- `0x314D` (no offset)
- `0x08000000 + 0x314D` (STM32 flash base + offset)
- `0x00000000 + 0x314D` (zero base)

**Step 4:** If all fail, need JTAG/SWD hardware approach

---

## ⚠️ Important Notes

### Backup First!
Before writing to flash:
1. Read current value: `byte[] backup = protocol_struct.Read(0x314D, 1);`
2. Save it somewhere
3. If radio bricks, you know what to restore

### Test Carefully!
- Write to flash can be permanent
- Wrong address = bricked radio
- Always have backup radio or be prepared to JTAG recover

---

**Start with the config memory test first! Don't jump to flash writes until we confirm config doesn't work!**
