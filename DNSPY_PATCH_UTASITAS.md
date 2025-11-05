# dnSpy Patch Utasítás - VÉGLEGES MEGOLDÁS

## 🎯 Mit találtunk

A firmware validáció a **`wfm_progress.Updata()`** metódusban van!

**Osztály:** `K7.wfm_progress`
**Metódus:** `Updata()` (RID: 829, Token: 0x0600033D)

---

## ✅ PATCH - 2 verzió

### VERZIÓ A: Teljes bypass (LEGEGYSZERŰBB)

A teljes `Updata()` metódust cseréld le erre:

```csharp
public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;

        // PATCH: Bypass validation
        try
        {
            array = File.ReadAllBytes(path);
        }
        catch (Exception ex)
        {
            array = null;
        }

        if (array != null)
        {
            if (this.downloadFileEx(array))
            {
                MessageBox.Show(this.GetLang("write_success"));
            }
            else
            {
                MessageBox.Show(this.GetLang("write_fail"));
            }
        }
        else
        {
            MessageBox.Show(this.GetLang("文件版本错误"));
        }
    }
}
```

---

### VERZIÓ B: Minimális patch (BIZTONSÁGOSABB)

Csak egy részt adj hozzá a meglévő kódhoz:

**KERESS RÁ ERRE A RÉSZRE:**
```csharp
        if (array == null)
        {
            try
            {
                array = this.PareUpdataFile1(path);
            }
            catch (Exception ex)
            {
                array = null;
            }
        }
        if (array != null)
```

**MÓDOSÍTSD ERRE:**
```csharp
        if (array == null)
        {
            try
            {
                array = this.PareUpdataFile1(path);
            }
            catch (Exception ex)
            {
                array = null;
            }
        }

        // ⭐ PATCH: Ha validáció sikertelen, bypass!
        if (array == null)
        {
            try
            {
                array = File.ReadAllBytes(path);
            }
            catch (Exception ex2)
            {
                array = null;
            }
        }

        if (array != null)
```

---

## 📋 Lépések a dnSpy-ban

### 1. Nyisd meg a dnSpy-t és a TK11.exe-t

```bash
E:\AI\tk11\dnSpy\dnSpy.exe
File → Open → E:\AI\tk11\TK11.exe
```

### 2. Navigálj a metódushoz

A bal oldali fában:
```
TK11
└─ K7
   └─ wfm_progress
      └─ Updata : void(void)  ← KATTINTS IDE!
```

VAGY gyorsabb:
- Nyomd meg: **`Ctrl+Shift+K`**
- Keress: **`文件版本错误`**
- Dupla klikk az eredményen → `wfm_progress.Updata()`

### 3. Szerkeszd a metódust

1. **Jobb klikk** az `Updata` metóduson (a kódban vagy a bal oldali fában)
2. Válaszd: **"Edit Method (C#)..."**
3. A megnyíló ablakban látod a teljes metódus kódját
4. Módosítsd **VERZIÓ A** vagy **VERZIÓ B** szerint
5. Klikk: **"Compile"** (alul jobbra)

### 4. Mentsd el

1. Ha sikeres volt a fordítás:
   - **File** → **Save Module**
   - Mentsd ide: `E:\AI\tk11\TK11_PATCHED_FINAL.exe`

2. Zárdd be a dnSpy-t

### 5. Teszteld

```bash
cd E:\AI\tk11

# Backup
copy TK11.exe TK11_ORIGINAL_FINAL.exe

# Patch használata
copy TK11_PATCHED_FINAL.exe TK11.exe

# Indítsd el
TK11.exe
```

Próbáld betölteni a patched firmware-t:
```
patched_firmware\TK11_PATCHED_USB_TX_ENABLED_20251103_114456.bin
```

**Ha nem jön "File version is Wrong" hiba → SIKER! 🎉**

---

## 🔧 Hibaelhárítás

### "Compilation failed"

**OK:** Szintaktikai hiba a kódban

**Megoldás:**
- Ellenőrizd, hogy minden kapcsos zárójel (`{}`) helyesen van-e
- Minden pontosvessző (`;`) megvan-e
- Nézd meg a pontos hibaüzenetet

### "Method is too complex to edit"

**OK:** A metódus túl hosszú

**Megoldás:**
- Használd a **VERZIÓ B** patch-et (kisebb változtatás)
- Vagy próbáld "Edit IL Instructions..." opcióval (haladó)

### Sikeres compile, de még mindig hiba

**OK:** Nem a patch-elt exe-t futtatod

**Megoldás:**
- Ellenőrizd: `TK11.exe` valóban a patch-elt verzió?
- Fájlméret/dátum ellenőrzés
- Próbáld újra a copy parancsot

---

## 📊 Mit csináltunk

### VERZIÓ A (Teljes bypass):
1. ❌ Kihagyjuk a `PareUpdataFile()` metódust (új formátum validáció)
2. ❌ Kihagyjuk a `PareUpdataFile1()` metódust (régi formátum validáció)
3. ✅ Közvetlenül beolvassuk a fájlt: `File.ReadAllBytes()`
4. ✅ Továbbítjuk a `downloadFileEx()` metódusnak

**Előny:** Egyszerű, rövid kód
**Hátrány:** Teljesen kihagyja a validációt

### VERZIÓ B (Minimális bypass):
1. ✅ Megpróbálja az új formátumot (`PareUpdataFile`)
2. ✅ Ha sikertelen, megpróbálja a régi formátumot (`PareUpdataFile1`)
3. ✅ **PATCH:** Ha még mindig sikertelen, nyers beolvasás
4. ✅ Továbbítjuk a `downloadFileEx()` metódusnak

**Előny:** Megtartja az eredeti validációt, csak fallback-et ad
**Hátrány:** Egy kicsit hosszabb kód

---

## 🎯 Ajánlás

**Kezdd a VERZIÓ B-vel** - ez biztonságosabb és kompatibilisebb.

Ha nem működik, próbáld a VERZIÓ A-t.

---

## ✅ Sikerkritériumok

### Patch sikeresen alkalmazva, ha:
1. ✅ dnSpy-ban sikeres compile
2. ✅ TK11.exe elindul (nincs crash)
3. ✅ Firmware betöltésekor **nincs** "File version is Wrong" hiba
4. ✅ A patched firmware feltölthető a rádióra

### Teljes siker, ha:
1. ✅ Firmware sikeresen flash-elve
2. ✅ USB mode konfiguráció betölthető
3. ✅ K38 csatornán PTT működik
4. ✅ **NINCS** "DISABLE" üzenet!

---

## 📞 Következő lépések a patch után

1. ✅ Patched firmware flash-elése
2. ✅ USB mode konfiguráció betöltése
3. ✅ Teszt dummy load-dal
4. ✅ Spektrum analizátor ellenőrzés

**Útmutató:** `FIRMWARE_FLASH_GUIDE.md`

---

## 🎉 Gratulálok!

Ha eljutottál eddig és sikerült a patch, akkor **befejeztük a projektet**!

A firmware USB TX unlock **MŰKÖDNI FOG**! 🚀

**73!** 📻
