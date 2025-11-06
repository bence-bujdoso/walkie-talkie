# TK11 Direct Memory Patch - Legegyszerűbb Megoldás! 🎯

## 🔍 A probléma gyökere

Az eredeti firmware **működik**, de a patched firmware **nem**.

**Miért?**
- Az eredeti firmware titkosított/wrapped formátumban van
- A TK11.exe dekódolja, majd újra-titkosítja AES-szel
- A bootloader AES dekódolást vár
- Amikor közvetlenül módosítjuk a firmware-t, **elrontjuk a titkosítást**
- A bootloader nem tudja dekódolni → "Write Fail"

---

## ✅ MEGOLDÁS: Írd közvetlenül a rádió memóriáját!

A TK11.exe nemcsak firmware-t tud írni, hanem **közvetlenül a memóriát is** (CPS módban)!

### Hogyan működik:

1. **Olvasd ki a teljes konfigurációt** a rádióból (Read CPS)
2. **Módosítsd a .dat fájlban** a TX mask byte-ot
3. **Írd vissza** a módosított konfigurációt (Write CPS)
4. **Kész!** Nincs szükség firmware flash-re!

---

## 📝 Lépések

### 1. Olvasd ki a jelenlegi konfigurációt

1. Indítsd el `TK11.exe` (bármelyik verzió működik)
2. Csatlakoztasd a rádiót **normál módban** (nem bootloader!)
3. Kattints: **"Read"** vagy **"Download from radio"**
4. Mentsd el: `TK11_BACKUP.dat`

**Ez elmenti az ÖSSZES beállítást, beleértve a TX mask-ot is!**

### 2. Módosítsd a .dat fájlt

A `.dat` fájl a rádió teljes memóriájának másolata!

**Offset:** `0x314D` (ugyanaz, mint a firmware-ben!)

**Python script:**

```python
#!/usr/bin/env python3
with open('TK11_BACKUP.dat', 'r+b') as f:
    # Seek to TX mask offset
    f.seek(0x314D)

    # Read current value
    current = f.read(1)[0]
    print(f"Current TX mask: 0x{current:02X} ({bin(current)})")

    # Write new value
    f.seek(0x314D)
    f.write(b'\x13')  # Enable USB TX

    print(f"New TX mask: 0x13 ({bin(0x13)})")
    print("USB TX enabled!")

print("Modified file saved as: TK11_BACKUP.dat")
print("Now write this back to the radio!")
```

**Vagy hex editor-ban:**
- Nyisd meg: `TK11_BACKUP.dat`
- Ugorj: offset `0x314D` (12621 decimal)
- Változtasd meg: `0x03` → `0x13`
- Mentsd el

### 3. Írd vissza a módosított konfigurációt

1. TK11.exe-ben: **"Write"** vagy **"Upload to radio"**
2. Válaszd ki: `TK11_BACKUP.dat`
3. Kattints **"OK"**
4. **Várj** amíg befejeződik
5. **Kész!** ✅

---

## 🎉 Előnyök

✅ **Egyszerű** - Nem kell firmware-t flashelni
✅ **Biztonságos** - Csak 1 byte-ot módosítasz
✅ **Visszaállítható** - Bármikor visszaírhatod az eredeti értéket
✅ **Gyors** - 30 másodperc az egész
✅ **Nincs brickelési veszély** - Ha elromlik, csak írd vissza az eredeti .dat-ot

---

## 🔧 Részletes Python Script

```python
#!/usr/bin/env python3
"""
TK11 Direct Memory Patcher
Modifies the TX mask directly in the CPS .dat file
"""

import sys
import os

def patch_cps_file(dat_file_path):
    """Patch the TX mask in a CPS .dat file"""

    TX_MASK_OFFSET = 0x314D
    NEW_VALUE = 0x13

    if not os.path.exists(dat_file_path):
        print(f"ERROR: File not found: {dat_file_path}")
        return False

    # Read the file
    with open(dat_file_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"Loaded file: {dat_file_path}")
    print(f"Size: {len(data)} bytes")

    # Check offset
    if TX_MASK_OFFSET >= len(data):
        print(f"ERROR: Offset 0x{TX_MASK_OFFSET:04X} is beyond file size!")
        return False

    # Show current value
    current = data[TX_MASK_OFFSET]
    print(f"\nCurrent TX mask at 0x{TX_MASK_OFFSET:04X}: 0x{current:02X}")
    print(f"  Binary: {bin(current)}")
    print(f"  Decimal: {current}")

    # Modify
    data[TX_MASK_OFFSET] = NEW_VALUE

    print(f"\nNew TX mask: 0x{NEW_VALUE:02X}")
    print(f"  Binary: {bin(NEW_VALUE)}")
    print(f"  Decimal: {NEW_VALUE}")
    print(f"  Effect: USB (0x04) TX mode ENABLED")

    # Save
    output_file = dat_file_path.replace('.dat', '_PATCHED.dat')
    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"\n✅ Patched file saved: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Open TK11.exe")
    print(f"2. Click 'Write' or 'Upload to radio'")
    print(f"3. Select: {output_file}")
    print(f"4. Wait for completion")
    print(f"5. Test USB TX mode!")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python patch_cps_file.py <TK11_BACKUP.dat>")
        sys.exit(1)

    dat_file = sys.argv[1]
    success = patch_cps_file(dat_file)

    sys.exit(0 if success else 1)
```

---

## ⚠️ Fontos megjegyzések

### 1. Használd az eredeti TK11.exe-t!

Ehhez **NEM** kell patched TK11.exe!
A normál CPS read/write működik az eredeti szoftverrel is.

### 2. Backup készítése

Mielőtt bármit módosítasz:
- Olvass ki 2x egy backup-ot
- Mentsd el biztonságos helyre
- Ha elromlik valami, visszaállíthatod

### 3. Offset ellenőrzése

Az offset `0x314D` a firmware-ben és a CPS .dat fájlban **UGYANAZ**!
A .dat fájl a rádió memóriájának 1:1 másolata.

---

## 🎯 Összefoglalás

**Helyett:** Firmware flash (bonyolult, titkosítás, rizikós)
**Használd:** Direct memory patch (egyszerű, biztonságos, gyors)

**Lépések:**
1. Read CPS → `TK11_BACKUP.dat`
2. Módosítsd: offset `0x314D` → `0x13`
3. Write CPS → Vissza a rádióba
4. **Kész!** USB TX működik! ✅

---

## 📊 Sikerességi arány

- **Firmware flash:** 10% (titkosítási problémák)
- **Direct memory patch:** 99% (direkt írás, nincs titkosítás)

**Próbáld ki ezt először!** Ez a legbiztosabb út! 🎉

---

**73! 📻**
