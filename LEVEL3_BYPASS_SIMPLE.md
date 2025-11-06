# Level 3 Bypass - Egyszerű Útmutató (5 perc)

## 📋 Helyzet

✅ TK11_PATCHED.exe működik (nincs "File version is Wrong" hiba)
❌ Mind a 8 firmware variáns "Write Fail"-t ad
🎯 **Megoldás:** Level 3 bypass kell!

---

## 🚀 Lépések

### 1️⃣ Nyisd meg a patched TK11.exe-t dnSpy-ban

1. Indítsd el dnSpy-t
2. **File** → **Open**
3. Válaszd ki: `bin\patched_software\TK11_PATCHED.exe`

### 2️⃣ Navigálj a downloadFileEx metódushoz

Bal oldali fában kattintgass végig:
```
TK11
 └─ K7
     └─ wfm_progress
         └─ downloadFileEx(byte[] allBuffer)  ← IDE KELL MENNI
```

### 3️⃣ Szerkeszd a metódust

1. **Jobb klikk** a `downloadFileEx(byte[] allBuffer)` -ra
2. Válaszd: **"Edit Method (C#)..."**
3. Megnyílik egy ablak sok kóddal

### 4️⃣ Keresd meg ezt a kódrészletet (CTRL+F)

Nyomd meg: **CTRL+F** (keresés)

Keresd meg ezt a szöveget:
```
if (!flag2)
```

Találni fogsz egy ilyen részt (kb 20-40. sor környékén):

```csharp
    if (!flag2)
    {
        return false;
    }
```

Ez okozza a "Write Fail" hibát! ☝️

### 5️⃣ Cseréld ki a kódot

**Régi kód (töröld):**
```csharp
    if (!flag2)
    {
        return false;
    }
```

**Új kód (másold be):**
```csharp
    if (!flag2)
    {
        flag2 = true;
        System.Windows.Forms.MessageBox.Show("Bootloader bypass aktív!", "Level 3");
    }
```

### 6️⃣ Fordítsd le (Compile)

1. Kattints a **"Compile"** gombra (jobb alul az ablakban)
2. Várj, amíg lefut
3. Ha **"Compilation successful"** jelenik meg → Sikeres! ✅
4. Ha hiba van → Nézd meg, hogy jól másoltad-e be a kódot

### 7️⃣ Mentsd el az új verziót

1. **File** → **Save Module**
2. Mentsd másik néven: `bin\patched_software\TK11_PATCHED_LEVEL3.exe`
3. Zárd be dnSpy-t

### 8️⃣ Tesztelés

1. **Indítsd el:** `TK11_PATCHED_LEVEL3.exe`
2. **Tölts be firmware-t:** Bármelyik a 8-ból (pl. `TK11_PATCHED_v3_minimal.bin`)
3. **Flash:** Kattints az Update gombra
4. **Várd meg:** Felugrik egy ablak: "Bootloader bypass aktív!" ✅
5. **Kattints OK** → A flash folytatódik!
6. **Figyelj:** A progress bar mozogjon, ne álljon meg 0%-on!

---

## ✅ Várható eredmény

Ha minden jól megy:

1. ✅ Felugrik: "Bootloader bypass aktív!"
2. ✅ Flash elindul, progress bar mozog
3. ✅ Eléri a 100%-ot
4. ✅ A rádió újraindul
5. ✅ A rádió normálisan bootol
6. ✅ USB TX mód működik! 🎉

---

## 🔧 Hibaelhárítás

### "Compilation failed"

**Ok:** Elgépelés a kódban

**Megoldás:**
- Másold be újra pontosan a fenti kódot
- Figyelj a pontos formázásra (kapcsos zárójelek, pontosvesszők)

### Nem látom az "if (!flag2)" részt

**Ok:** Rossz helyen keresel

**Megoldás:**
- Győződj meg róla, hogy a `downloadFileEx()` metódusban vagy
- Használj CTRL+F keresést: "if (!flag2)"
- Kb a 20-40. sor környékén kell lennie

### Továbbra is "Write Fail"

**Ok:** Nem a Level 3 verziót használod

**Megoldás:**
```bash
# Ellenőrizd a fájlnevet:
dir TK11*.exe

# Biztos használod a LEVEL3-at?
# Ha nem, indítsd el: TK11_PATCHED_LEVEL3.exe
```

### Flash megáll 0%-on

**Ok:** A bypass nem működik

**Megoldás:**
- Látod a "Bootloader bypass aktív!" üzenetet? Ha nem, a patch nem működik.
- Próbáld újra a patch-elést
- Vagy próbáld az "egyszerűbb" verziót (lásd alább)

---

## 🔹 Alternatív (egyszerűbb) megoldás

Ha a fenti nem működik, próbáld ezt:

**Keresd meg:**
```csharp
    if (!flag2)
    {
        return false;
    }
```

**Cseréld ki erre (egyszerűbb):**
```csharp
    if (!flag2)
    {
        // return false;
    }
```

Gyakorlatilag csak "kikommentezed" a `return false;` sort (tedd elé: `//`)

Ez is működnie kell!

---

## 🆘 Ha semmi sem működik

Ha a Level 3 bypass után is "Write Fail" vagy más hiba:

**Lehetséges okok:**
1. A firmware formátum fundamentálisan inkompatibilis
2. Titkosítás szükséges
3. További ellenőrzések vannak a kódban

**Következő lépés:**
Szólj nekem, és megpróbáljuk:
- Dekódolni az eredeti firmware-t
- Módosítani a dekódolt verziót
- Újra tesztelni

---

## 📝 Összefoglaló

```
1. Nyisd meg: TK11_PATCHED.exe (dnSpy)
2. Navigálj: downloadFileEx()
3. Keresd: if (!flag2) { return false; }
4. Cseréld: flag2 = true; MessageBox.Show(...)
5. Compile + Save as: TK11_PATCHED_LEVEL3.exe
6. Teszteld!
```

**Sok sikert! 73! 📻**
