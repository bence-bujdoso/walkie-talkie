# Engineering Mode - Finding Memory Write Functions

## ✅ SUCCESS: You're In!

**Password:** `tk11` or `unlock`
**Status:** Engineering mode enabled (`main.gEngineerMode = true`)

---

## 🔍 Next Steps: Find Memory Write Functions

### Step 1: Explore the GUI

**Look for:**
- New menu items that appeared
- New buttons/tabs
- "Memory" or "Flash" options
- "Read" / "Write" buttons
- Text boxes for address/data input
- Debug/service tabs

**Take screenshots or note what new options are available!**

---

### Step 2: Search Code for Memory Write Functions

In dnSpy, search for these patterns:

#### Search #1: "gEngineerMode" Usage
```
1. Press Ctrl+F (Find)
2. Search for: gEngineerMode
3. Look for code that checks: if (gEngineerMode)
4. This will show what features are unlocked
```

**Example pattern to look for:**
```csharp
if (main.gEngineerMode)
{
    // Special functions available here!
    this.button_WriteMemory.Enabled = true;
    this.button_ReadMemory.Enabled = true;
}
```

#### Search #2: Memory Write Functions
```
1. Press Ctrl+Shift+F (Search in all types)
2. Search for: WriteMemory
3. Also search for: WriteFlash, DirectWrite, ServiceWrite
```

#### Search #3: Protocol Functions
```
Look in protocol_struct class for:
- WriteMemory
- ReadMemory
- WriteFlash
- ReadFlash
- DirectWrite
- ServiceCommand
```

---

### Step 3: Look for Address Input Fields

**In the GUI (Engineering mode enabled):**
- Look for text boxes labeled "Address" or "Addr"
- Look for text boxes labeled "Data" or "Value"
- Look for "Read" / "Write" buttons near these fields

**Common layouts:**
```
[Address: 0x________] [Read] [Write]
[Data:    0x________]
```

Or:
```
Memory Operations:
Address: [_______]
Data:    [_______]
[Read Memory] [Write Memory]
```

---

### Step 4: Check Menu Items

With Engineering mode enabled, check if new menu items appeared:

- **Tools** menu
- **Service** menu
- **Debug** menu
- **Engineering** menu
- **Advanced** menu

Click through and see what options are there!

---

## 🎯 What We're Looking For

### Perfect Scenario: Direct Memory Write UI

**If you find something like this:**
```
Memory Write:
  Address: [0x314D]
  Value:   [0x17]
  [Write to Radio]
```

**Then you can:**
1. Enter address: `0x314D` (or try `12621` decimal)
2. Enter value: `0x17` (or `23` decimal)
3. Click Write
4. Done! USB TX should work!

---

### Alternative: Code-Based Approach

If no obvious UI, we'll need to:
1. Find the memory write function in code
2. Call it programmatically
3. Or create a simple UI to call it

---

## 📝 Report Back

**Tell me what you see:**

1. **GUI Changes:**
   - Any new buttons/menus?
   - Any address/data input fields?
   - Any "Memory" or "Flash" options?

2. **Code Search Results:**
   - Did you find `WriteMemory` functions?
   - What's in the `protocol_struct` class?
   - Any functions that take address and data parameters?

---

## 🔍 Quick Code Search Guide

### In dnSpy:

```
1. Open Assembly Explorer (left panel)
2. Expand: TK11 → Namespaces → K7
3. Find class: protocol_struct
4. Look through methods for:
   - Read/Write
   - Memory
   - Flash
   - Direct
   - Service
```

**Example methods to look for:**
```csharp
public static bool WriteMemory(uint address, byte value)
public static bool WriteFlash(uint address, byte[] data)
public static bool DirectWrite(byte[] command)
public static byte[] ReadMemory(uint address, int length)
```

---

## 🎯 Target Operation

**What we need to do:**

```
Function: WriteMemory (or similar)
Address:  0x314D (12621 decimal)
Value:    0x17 (23 decimal)
Effect:   Enable USB TX mode
```

---

## ⚡ Quick Test Commands

If you find a memory write function, we need to:

1. **Connect radio** (in normal mode)
2. **Call memory write function:**
   - Address: `0x314D`
   - Value: `0x17`
3. **Restart radio**
4. **Test USB TX** on K38 channel

---

## 🚨 Important Notes

### Flash Address vs File Offset

The address `0x314D` might need adjustment:

- **Firmware file offset:** `0x314D` (what we found in analysis)
- **Flash memory address:** Might be `0x08000000 + 0x314D` (STM32 typical)
- **RAM address:** Different if firmware copies to RAM

**Try these variations:**
- `0x314D` (decimal: 12621)
- `0x0800314D` (if STM32 flash base)
- Look for other channels with USB mode working - read their config

### Backup Current Value

Before writing, try to:
1. Read current value at 0x314D
2. Save it
3. Then write 0x17
4. If problem, restore original value

---

**Start exploring Engineering mode and report back what you find!** 🔍
