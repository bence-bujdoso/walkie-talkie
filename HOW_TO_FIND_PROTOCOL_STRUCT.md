# How to Find protocol_struct and Memory Write Functions in dnSpy

## 📋 Step-by-Step Guide

### Step 1: Navigate to protocol_struct Class

1. **In dnSpy, look at the left panel** (Assembly Explorer)
2. You should see a tree structure like:
   ```
   ▼ TK11 (or TK11.exe)
     ▼ {} (curly braces icon - this is the global namespace)
       ▼ K7 (namespace)
         ▶ main
         ▶ wfm_progress
         ▶ protocol_struct  ← FIND THIS ONE!
         ▶ Util
         ... (other classes)
   ```

3. **Click on `protocol_struct`** to expand it
4. You'll see all the methods (functions) inside it

### Step 2: Look for Memory/Write Functions

Once you expand `protocol_struct`, look for methods with names like:
- `WriteMemory`
- `ReadMemory`
- `WriteFlash`
- `ReadFlash`
- `DirectWrite`
- `SendCommand`
- `packetFileEx` (we already know this one exists)

### Step 3: Alternative Search Method

If you can't find protocol_struct easily:

1. **Press `Ctrl+Shift+F`** (Search in all types)
2. In the search box, type: **`protocol_struct`**
3. Click search
4. Double-click on the **class** result (not the variable)
5. This will open the class definition

### Step 4: Search for Specific Functions

1. Once you're viewing `protocol_struct` class
2. **Press `Ctrl+F`** (Find in current file)
3. Search for: **`Write`**
4. Press `F3` to find next occurrence
5. Look through all methods that have "Write" in their name

---

## 🔍 What to Look For

### Good Signs:

Functions that look like this:
```csharp
public static bool WriteMemory(uint address, byte value)
public static bool WriteFlash(int address, byte[] data)
public static bool DirectWrite(byte command, byte[] data)
```

### What We Need:

A function that:
- Takes an **address** parameter (uint, int, or long)
- Takes a **value** or **data** parameter (byte, byte[], or int)
- Sends commands to the radio

---

## 📝 Report Back Template

Once you find it, tell me:

**Method Name:** `________`
**Parameters:** `________`
**Return Type:** `________`

For example:
```
Method Name: WriteFlash
Parameters: (uint address, byte value)
Return Type: bool
```

---

## 🎯 Alternative: Show Me ALL Methods

If you're not sure what you're looking for, you can:

1. Expand `protocol_struct` in the tree
2. Take a screenshot showing all the methods
3. Or list them here (copy/paste the method names)

I'll tell you which one to use!

---

## ⚡ Quick Visual Guide

**What you should see in dnSpy:**

```
Assembly Explorer (left panel):
│
├─ TK11.exe
│  └─ {}
│     └─ K7
│        ├─ main
│        ├─ wfm_progress
│        │  ├─ downloadFileEx(byte[])     ← We modified this
│        │  ├─ Updata()
│        │  └─ ...
│        ├─ protocol_struct                ← LOOK IN HERE!
│        │  ├─ SendUpdataConnectReq(...)
│        │  ├─ packetFileEx(...)
│        │  ├─ WriteMemory(...)            ← Looking for this!
│        │  ├─ ReadMemory(...)             ← Or this!
│        │  └─ ...
│        └─ Util
│           └─ ...
```

---

## 🚨 If You Can't Find It

If `protocol_struct` isn't in K7 namespace, try:

1. **Search all namespaces:**
   - Expand other namespaces in the tree
   - Or use `Ctrl+Shift+F` and search for `protocol_struct`

2. **Look for similar names:**
   - `Protocol`
   - `RadioProtocol`
   - `CommProtocol`
   - `SerialProtocol`

3. **Search for known functions:**
   - `Ctrl+Shift+F` → Search: `packetFileEx`
   - This function is in `protocol_struct`, so finding it will show you where the class is

---

**Try these steps and report back what you find!** 🔍
