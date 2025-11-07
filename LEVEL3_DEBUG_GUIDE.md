# Level 3 Bypass - Debug Útmutató

## 🚨 Probléma

A patch után is:
- ❌ Nem ugrik fel a "Bootloader bypass aktív!" üzenet
- ❌ "Write Fail" azonnal megjelenik (0%-on)
- ✅ De biztos vagy benne, hogy a patched verziót futtatod

## 🔍 Mi lehet a probléma?

### 1. A Compile sikertelen volt

Ha a dnSpy-ban kattintottál a "Compile" gombra, MEGNÉZTED hogy mit írt ki?

**Ellenőrzés:**
- Sikeres compile: "Compilation successful" vagy "OK" üzenet
- Sikertelen: Piros hibaüzenetek az alján

**Ha sikertelen volt:**
- Szintaxis hiba van a kódban
- Próbáld újra, pontosan másolva

### 2. Rossz helyre került a kód

**Tényleg a `downloadFileEx()` metódusban vagy?**

Ellenőrzés:
1. Nézd meg az ablak tetején: `downloadFileEx(byte[] allBuffer)` -nak kell lennie
2. Ha valami más van (pl. `Updata()`), akkor rossz helyen vagy!

### 3. Nem találod az `if (!flag2)` részt

**Van több `if (!flag2)` is a kódban!**

A JÓ helyen ez van ELŐTTE (kb 10 sorral feljebb):

```csharp
Random random = new Random();
wfm_progress.seed = random.Next(0, 16);
for (int i = 0; i < 5; i++)
{
    try
    {
        flag2 = protocol_struct.SendUpdataConnectReq(...);
    }
    ...
}
if (!flag2)  // ⭐ EZ AZ!
{
    return false;
}
```

**Keresd meg azt az `if (!flag2)` részt, ami a `SendUpdataConnectReq` UTÁN van!**

### 4. Nem mentette el

**File → Save Module után tényleg elmentette?**

Ellenőrzés:
- Nézd meg a fájl dátumát: `bin\patched_software\TK11_PATCHED_LEVEL3.exe`
- A dátum MOST-nak kell lennie (amikor elmentetted)
- Ha régi → nem mentette el!

---

## ✅ Lépésről-lépésre ÚJRA (garantált működés)

### 1. Nyisd meg dnSpy-t ÚJRA

Zárd be teljesen, majd indítsd újra.

### 2. Tölts be: `TK11_PATCHED.exe`

(Nem a LEVEL3-at, hanem az eredeti patched-et!)

### 3. Navigálj: `K7` → `wfm_progress` → `downloadFileEx(byte[] allBuffer)`

**FONTOS:** Nézd meg az ablak tetején hogy `downloadFileEx` van-e!

### 4. Jobb klikk → "Edit Method (C#)..."

### 5. Görgets le kb a 20-40. sorig

Keresd meg ezt a BLOKKOT:

```csharp
bool flag2 = false;
if (protocol_struct.check_boot_ver(protocol_struct.boot_version))
{
    Random random = new Random();
    wfm_progress.seed = random.Next(0, 16);
    for (int i = 0; i < 5; i++)
    {
        try
        {
            flag2 = protocol_struct.SendUpdataConnectReq(protocol_struct.boot_version, wfm_progress.seed);
        }
        catch (Exception ex)
        {
            flag2 = false;
        }
        if (protocol_struct.boot_version == "4.00.03")
        {
            break;
        }
        if (flag2)
        {
            break;
        }
    }
    if (!flag2)  // ⭐⭐⭐ EZ A FONTOS SOR! ⭐⭐⭐
    {
        return false;  // ⭐ EZT KELL MEGVÁLTOZTATNI
    }
```

### 6. CSAK ezt a részt változtasd meg:

**RÉGI (töröld):**
```csharp
    if (!flag2)
    {
        return false;
    }
```

**ÚJ (írd be):**
```csharp
    if (!flag2)
    {
        flag2 = true;
        System.Windows.Forms.MessageBox.Show("Bootloader bypass aktív!", "Level 3");
    }
```

**FONTOS:**
- A `flag2 = true;` sorban KELL a pontosvessző!
- A `MessageBox.Show` EGÉSZ egy sorban legyen!
- A kapcsos zárójelek `{}` maradjanak meg!

### 7. Compile

Kattints: **"Compile"** gomb (jobb alul)

**VÁRJ a kiírásra:**
- Ha: "Compilation successful" → SIKERES ✅
- Ha: ERROR... valami hiba → SIKERTELEN ❌

**Ha sikertelen:**
- Olvasd el a hiba üzenetet
- Valószínűleg elgépelés van
- Próbáld újra

### 8. Save Module

**CSAK HA A COMPILE SIKERES VOLT!**

1. **File** menü
2. **Save Module...**
3. Mentsd másik néven: `TK11_PATCHED_LEVEL3.exe`
4. Ellenőrizd a fájl dátumát!

### 9. Tesztelés

1. **ZÁRD BE dnSpy-t teljesen**
2. **Indítsd el:** `TK11_PATCHED_LEVEL3.exe`
3. Tölts be firmware-t
4. Kattints Flash/Update
5. **AZONNAL fel kell ugrani:** "Bootloader bypass aktív!"

---

## 🔍 További Debug Tippek

### Ha továbbra sem ugrik fel az üzenet:

**Próbáld az egyszerűbb verziót:**

Változtasd meg csak erre:

```csharp
    if (!flag2)
    {
        System.Windows.Forms.MessageBox.Show("TESZT!", "TESZT");
        return false;
    }
```

Ha ez felugrik → a kód helyén van!
Ha ez sem ugrik fel → rossz helyen vagy!

### Vagy próbáld ezt:

**Tedd a MessageBox-ot a metódus ELEJÉRE:**

A `downloadFileEx()` metódus legelső sora legyen:

```csharp
public bool downloadFileEx(byte[] allBuffer)
{
    System.Windows.Forms.MessageBox.Show("downloadFileEx elindult!", "DEBUG");
    // ... többi kód
}
```

Ha ez felugrik → jó helyen vagy, tovább debuggolhatsz!
Ha ez sem ugrik fel → nem a patched verziót futtatod!

---

## 🆘 Ha semmi sem működik

**Küldj screenshot-ot vagy írj le PONTOSAN:**

1. dnSpy ablak tetején mi van írva? (metódus neve)
2. Mit látsz amikor Compile-t nyomsz? (hibaüzenet vagy OK?)
3. A fájl dátuma: `TK11_PATCHED_LEVEL3.exe` (mai dátum?)
4. Mi van az exe ablak tetején amikor futtatod? (fájlnév)

És folytatjuk a debuggolást! 🔧

---

**Próbáld újra a fenti lépésekkel, és szólj mi történik!** 📻
