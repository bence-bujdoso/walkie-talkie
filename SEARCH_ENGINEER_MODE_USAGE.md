# How to Find What Engineering Mode Unlocks

## 🎯 Goal

Find all the places in the code that check `gEngineerMode` to see what features it unlocks.

---

## 📋 Step-by-Step

### Step 1: Search for gEngineerMode Usage

1. **In dnSpy, press `Ctrl+F`** (or `Ctrl+Shift+F` for global search)
2. In the search box, type: **`gEngineerMode`**
3. Make sure **"Match whole word"** is unchecked (to find all uses)
4. Click **"Search"** or press Enter

### Step 2: Look Through Results

You'll see multiple results. Look for patterns like:

#### Pattern 1: Enabling Hidden Features
```csharp
if (main.gEngineerMode)
{
    this.button_HiddenFeature.Visible = true;
    this.menuItem_Advanced.Enabled = true;
}
```

#### Pattern 2: Unlocking Functions
```csharp
if (main.gEngineerMode)
{
    // Allow direct memory access
    this.WriteMemoryToRadio(address, value);
}
```

#### Pattern 3: Showing Hidden UI
```csharp
this.tabPage_Engineering.Visible = main.gEngineerMode;
```

---

## 🔍 What to Look For

### Good Signs:

1. **Buttons or menu items being enabled:**
   ```csharp
   someButton.Enabled = main.gEngineerMode;
   someMenuItem.Visible = main.gEngineerMode;
   ```

2. **Hidden tabs or panels:**
   ```csharp
   tabPage_Advanced.Visible = main.gEngineerMode;
   panel_Service.Enabled = main.gEngineerMode;
   ```

3. **Function calls that are gated:**
   ```csharp
   if (main.gEngineerMode)
   {
       this.DirectWriteFunction();
   }
   ```

---

## 📝 Example Results

You might see something like:

```csharp
// Result 1: In main.cs
public static bool gEngineerMode = false;  ← Definition

// Result 2: In wfm_main.cs
if (main.gEngineerMode)
{
    this.toolStripButton_Service.Visible = true;
}

// Result 3: In wfm_progress.cs
if (main.gEngineerMode)
{
    this.button_WriteFlash.Enabled = true;
}
```

---

## 🎯 What We're Looking For

Specifically, look for:
- **Memory write functions** being unlocked
- **Flash write functions** being unlocked
- **Service commands** being enabled
- **Hidden buttons/menus** becoming visible

---

## 📊 Report Back

Tell me:
1. **How many results** did you find for `gEngineerMode`?
2. **What features** are being unlocked? (copy the code snippets)
3. **Any promising function names** like WriteMemory, WriteFlash, etc.?

---

## ⚡ Quick Method

**Alternative approach:**

1. Right-click on `gEngineerMode` in the code
2. Select **"Analyze"**
3. In the Analyzer window, look for **"Used By"**
4. This shows everywhere the variable is used!

---

## 🚨 Tip

The "Hide Param" tab you found is probably one thing unlocked by Engineering mode. But there should be more! Keep searching to find memory write functions.

---

**Do this search and tell me what you find!** 🔍
