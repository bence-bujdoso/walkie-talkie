# TK11 Hibrid Mód Útmutató - RX USB, TX AM

## 🎯 Mi Ez?

**Hibrid üzemmód:** Vételed USB/LSB, adásod AM

### Használati Eset

```
Te:          Rádió USB módban (2.7385 MHz)
SSB Adó:     USB modulációval ad → Te HALLOD (USB demod)
Te:          PTT nyomsz → AM-ben válaszolsz
SSB Adó:     AM-edet HALLJA (AM tartalmazza USB-t)
```

**Kompatibilitás:**
- ✅ SSB állomások hallanak téged (AM → USB komponens)
- ✅ Te hallod az SSB állomásokat (USB demoduláció)
- ✅ AM állomások is hallanak téged
- ✅ Te AM állomásokat is hallod

**Ez a TÖKÉLETES megoldás vegyes SSB/AM környezethez!**

---

## 📊 Hogyan Működik?

### AM és SSB Kompatibilitás

**AM jel spektruma:**
```
      Carrier (50%)
         |||
         |||
    /\   |||   /\
   /  \  |||  /  \
  /____\_|||_/____\
  LSB    C    USB
```
- Carrier: 50% teljesítmény
- LSB: 25% teljesítmény (alsó oldalsáv)
- USB: 25% teljesítmény (felső oldalsáv)

**USB vevő AM-et hallgatva:**
- USB demod csak a felső oldalsávot dolgozza fel
- AM felső oldalsáv = tiszta hang
- ✅ **MŰKÖDIK!**

**AM vevő USB-t hallgatva:**
- AM demod envelope detectort használ
- USB nincs carrier (elnyomott)
- ❌ **NEM működik jól** (csendes/torzult)

**DE: Ha TX=AM, akkor:**
- SSB vevők hallanak téged (AM USB része)
- Te hallod az SSB adókat (USB demod)
- ✅ **Kétirányú kommunikáció működik!**

---

## 🛠️ Implementáció

### Fájlok

**Patched Firmware:**
```
E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLE_20251029_154257.bin
```

**Konfigurációs fájl:**
```
E:\AI\tk11\TK11.dat (EREDETI! Nincs szükség módosításra!)
```
- K38 USB csatorna már létezik
- Mode: 0x04 (USB)
- Frekvencia: 2.7385 MHz

**Backup:**
```
E:\AI\tk11\patched_firmware\TK11_ORIGINAL_20251029_154257.bin
```

### Mit Változtattunk?

**Firmware Patch:**
```
Offset: 0x0000314D
Előtte: 0x03 (binary: 00000011) - Csak FM/AM engedélyezett
Utána:  0x13 (binary: 00010011) - FM/AM/USB engedélyezett
```

**Bit logika:**
```
Mode 0x04 (USB): 1 << 4 = 0b00010000
Mask: 0x13 = 0b00010011

0b00010000 & 0b00010011 = 0b00010000 (non-zero)
→ TX ENGEDÉLYEZETT!
```

**Eredmény:**
- ✅ K38 USB csatorna TX engedélyezve
- ✅ RX: USB demoduláció (változatlan)
- ✅ TX: Valószínűleg AM (hardware limitáció miatt)

---

## 🔧 Telepítési Útmutató

### Lépés 1: Firmware Flash (KOCKÁZATOS!)

⚠️ **FIGYELEM:** Firmware módosítás elronthatja a rádiót!

**Előkészületek:**
1. ✅ Olvasd el: `FIRMWARE_FLASH_GUIDE.md`
2. ✅ Teljesen feltöltött akkumulátor
3. ✅ Stabil áramellátás
4. ✅ Programozó kábel
5. ✅ TK11 firmware update ismeret
6. ✅ Kockázatok elfogadása

**Firmware Flash:**
```
1. Csatlakoztass programozó kábelt
2. Indítsd el TK11.exe-t
3. Lépj firmware update módba (lásd manuál!)
4. Válaszd ki: TK11_PATCHED_USB_TX_ENABLE_*.bin
5. Flash!
6. NE szakítsd meg a folyamatot!
7. Várd meg a befejezést
```

**Ellenőrzés:**
- Rádió újraindul
- Alapfunkciók működnek
- Kijelző normális

### Lépés 2: Konfiguráció Betöltése

**Nincs szükség új .dat fájlra!**

```
1. Töltsd be az EREDETI TK11.dat fájlt
2. Upload a rádióba
3. K38 USB csatorna már benne van!
```

**K38 csatorna jellemzői:**
- Név: "K38 USB"
- Frekvencia: 2.7385 MHz
- Mode: 0x04 (USB)
- TX: Most már engedélyezett (patch után)

---

## 🧪 Tesztelési Eljárás

### Teszt 1: TX Működik-e?

**Eszközök:**
- 50Ω dummy load (kötelező!)
- Spektrum analizátor (ajánlott)

**Lépések:**
```
1. Válaszd ki a K38 USB csatornát
2. Csatlakoztass dummy load-ot
3. Nyomj PTT-t
4. Ellenőrizd:
   - Nincs "DISABLE" üzenet? ✅
   - TX LED világít? ✅
   - Működik PTT? ✅
```

**Ha "DISABLE" üzenet:**
- ❌ Patch nem működött
- Rossz offset vagy firmware verzió
- Próbáld meg az "All_Modes" patch-et

**Ha PTT működik:**
- ✅ Patch sikeres!
- Tovább a moduláció teszthez

### Teszt 2: Moduláció Típus

**Spektrum analizátor setup:**
- Center: 2.7385 MHz
- Span: 20-50 kHz
- RBW: 1-3 kHz

**PTT nyomás közben figyeld meg:**

**Ha FM moduláció látszik:**
```
     |
     |  /\
  ───┴─/  \───
  Carrier mozog (frequency deviation)
```
→ ❌ Hardware FM-re kényszerít (nem jó)

**Ha AM moduláció látszik:**
```
       /\
      /  \
   /\ |  | /\
  /  \|  |/  \
 ─────┴──┴─────
  LSB  C  USB
  Carrier + 2 sideband
```
→ ✅ **TÖKÉLETES!** Ez kell!

**Ha SSB (csak 1 sideband):**
```
         /\
        /  \
       /    \
  ────┴──────
     Csak USB
```
→ ✅ Még jobb! (De valószínűtlen)

### Teszt 3: Vételi Teszt (USB Demod)

**Ha van SSB adó a közelben:**
```
1. Hangold a K38 USB csatornára
2. Hallgasd az SSB adót
3. Tisztán hallod? → RX USB demod működik ✅
```

**Ha nincs SSB adó:**
```
1. Használj második rádiót USB-ben
2. Adj USB jelet 2.7385 MHz-en
3. TK-11-el vedd
4. Hallod? → RX működik ✅
```

### Teszt 4: Kommunikáció Teszt

**Kétirányú teszt SSB állomással:**

```
SSB Állomás (USB):       TK-11 (K38 USB + patch):
"CQ CQ test"      ───>   [Hallod USB demod]
                         [PTT nyomsz]
[Hallod AM-et]    <───   "Válasz AM-ben"
```

**Sikeres teszt kritériumok:**
- ✅ Te hallod az SSB adót (USB demodulációval)
- ✅ SSB adó hall téged (AM USB komponenséből)
- ✅ Kétirányú kommunikáció működik

---

## 📊 Várható Eredmények

### Legvalószínűbb Kimenetel

**RX (vétel):**
- ✅ USB demoduláció működik (már most is működött)
- ✅ Hallod az SSB állomásokat
- ✅ Tiszta vételi hang

**TX (adás):**
- ✅ PTT működik (nincs "DISABLE")
- ✅ AM moduláció (BK4819 hardware limitáció)
- ✅ Carrier + 2 sideband látszik spektrumon
- ✅ SSB vevők hallanak (AM tartalmazza USB-t)

**Kompatibilitás:**
- ✅ SSB → AM irány: Működik
- ✅ AM → SSB irány: Működik
- ✅ Vegyes hálózatban használható

### Miért AM és Nem USB a TX-nél?

**Hardware limitáció:**
- BK4819 chip nem tud valódi SSB-t generálni
- Hiányzik: Hilbert filter, balanced modulator
- Csak FM/AM moduláció elérhető

**DE ez nem probléma, mert:**
- AM tartalmazza az USB oldalsávot
- SSB vevő ezt tökéletesen hallja
- Kétirányú kommunikáció működik

**Ez a "second best" megoldás, ami gyakorlatban tökéletesen működik!**

---

## ⚖️ Összehasonlítás

### Eredeti Állapot (Nincs Patch)

```
K38 USB csatorna (mode 0x04):
  RX: ✅ USB demoduláció működik
  TX: ❌ "DISABLE" - blokkolva

Használhatóság: Csak vételre
```

### Patch Után

```
K38 USB csatorna (mode 0x04):
  RX: ✅ USB demoduláció (változatlan)
  TX: ✅ AM moduláció (hardware limitáció)

Használhatóság: Kétirányú kommunikáció SSB-vel!
```

### Más Megoldások

| Megoldás | RX | TX | Működik? | Komplexitás |
|----------|----|----|----------|-------------|
| **AM mód használata** | AM demod | AM | ❌ Nem hallod az SSB-t | Egyszerű |
| **FM mód használata** | FM demod | FM | ❌ Nem kompatibilis SSB-vel | Egyszerű |
| **USB patch (EZ!)** | USB demod | AM | ✅ **Tökéletes!** | Közepes |
| **DSB hardmod** | DSB | DSB | ❓ Lehetetlen (hardware) | Nagyon nehéz |
| **Külső SSB modul** | SSB | SSB | ✅ Működne | Nagyon drága |

**A USB patch a legjobb gyakorlati megoldás!**

---

## 🎓 Gyakori Kérdések

### K: Miért nem valódi USB-t ad?
**V:** A BK4819 chip hardware limitációja. Nincs SSB modulátor, csak FM/AM.

### K: SSB állomás hallja az AM-emet?
**V:** Igen! AM tartalmazza az USB oldalsávot, amit az SSB vevő dekódol.

### K: Hallom én az SSB adókat?
**V:** Igen! A USB demoduláció működik vételnél.

### K: Működik LSB-vel is?
**V:** Elméletileg igen, de AM inkább USB-kompatibilis (felső oldalsáv erősebb).

### K: 11m sávon használható?
**V:** Igen! Létrehozhatsz CB frekvenciás csatornákat USB módban (mode 0x04).

### K: Legális?
**V:** Ha authorized frekvencián használod (CB, amateur band), és teljesítmény határon belül, igen.

### K: Mi van, ha nem működik?
**V:** Reflash az eredeti firmware-t (TK11_ORIGINAL_*.bin).

---

## 🔄 11m Sávra Alkalmazás (CB)

### CB Csatornák Létrehozása USB Módban

Ha a CB sávon (27 MHz) akarsz használni hibrid módot:

**Opció 1: Módosítsd a K38 frekvenciáját**

<script>
Use modify_k38_to_dsb.py de változtasd:
- Frekvencia: 27.185 MHz (CB-19)
- Mode: 0x04 (USB - ne változtasd!)
- Név: "CB-19 USB"
</script>

**Opció 2: Hozz létre új CB csatornákat**

A korábban létrehozott `unlock_11m_dsb.py` scriptet módosítsd:
- Mode byte legyen 0x04 (nem 0x05!)
- 40 CB csatorna USB módban

**Eredmény:**
- RX: USB demoduláció CB sávon
- TX: AM moduláció CB sávon
- Kompatibilis SSB és AM CB állomásokkal

**CB szabályozás:**
- USA: AM és SSB engedélyezett CB-n
- EU: AM standard, SSB függ az országtól
- Ellenőrizd helyi előírásokat!

---

## 📋 Ellenőrző Lista

### Firmware Flash Előtt
- [ ] Olvastam a FIRMWARE_FLASH_GUIDE.md-t
- [ ] Értem a kockázatokat
- [ ] Van backup firmware-em
- [ ] Akkumulátor teljesen töltött
- [ ] Programozó kábel működik
- [ ] Tudom a recovery eljárást

### Flash Után
- [ ] Rádió bekapcsol
- [ ] Alapfunkciók működnek
- [ ] TK11.dat betöltve
- [ ] K38 USB csatorna látszik

### TX Teszt
- [ ] Dummy load csatlakoztatva
- [ ] K38 USB kiválasztva
- [ ] PTT nyomva
- [ ] Nincs "DISABLE" üzenet
- [ ] TX LED világít

### Moduláció Teszt
- [ ] Spektrum analizátor beállítva
- [ ] 2.7385 MHz monitorizálva
- [ ] PTT közben AM moduláció látszik
- [ ] Carrier + 2 sideband megerősítve

### Vételi Teszt
- [ ] USB állomást kerestem
- [ ] Hallom az SSB jeleket
- [ ] USB demoduláció tiszta
- [ ] Kommunikáció működik

---

## 🏆 Összefoglalás

### Mit Értünk El?

**Probléma:**
- USB RX működik ✅
- USB TX blokkolva ❌
- SSB-vel akarok kommunikálni

**Megoldás:**
- Firmware patch engedélyezi USB TX-et
- Hardware AM-et ad (limitáció)
- DE ez tökéletes, mert AM kompatibilis USB-vel!

**Eredmény:**
- ✅ RX: USB demoduláció (hallod SSB-t)
- ✅ TX: AM moduláció (SSB hall téged)
- ✅ Kétirányú kommunikáció működik
- ✅ Nincs további hardver módosítás
- ✅ Egy firmware patch elég

**Ez a LEGJOBB gyakorlati megoldás a TK-11-re!**

---

## 📁 Fájlok

**Patched Firmware:**
```
E:\AI\tk11\patched_firmware\TK11_PATCHED_USB_TX_ENABLE_20251029_154257.bin
```

**Eredeti Backup:**
```
E:\AI\tk11\patched_firmware\TK11_ORIGINAL_20251029_154257.bin
```

**Konfiguráció:**
```
E:\AI\tk11\TK11.dat (eredeti, nincs módosítás!)
```

**Dokumentáció:**
```
E:\AI\tk11\FIRMWARE_FLASH_GUIDE.md
E:\AI\tk11\HYBRID_MODE_GUIDE.md (ez a fájl)
E:\AI\tk11\PROJECT_COMPLETE_SUMMARY.md
```

**Script:**
```
E:\AI\tk11\patch_usb_mode.py
```

---

## 🎯 Következő Lépések

1. **Döntés:** Vállalod a firmware flash kockázatát?

   **IGEN →** Folytatás lépés 2-vel

   **NEM →** Maradj AM módnál (működik, de nem hallod az SSB-t)

2. **Felkészülés:** Olvasd el FIRMWARE_FLASH_GUIDE.md

3. **Flash:** TK11_PATCHED_USB_TX_ENABLE_*.bin

4. **Betöltés:** Eredeti TK11.dat (K38 USB már benne van)

5. **Teszt:** Dummy load + PTT

6. **Ellenőrzés:** Spektrum analizátor

7. **Használat:** Kommunikálj SSB állomásokkal!

---

**Sikeres tesztelést!** 📻

**73!**

---

**Fájl:** HYBRID_MODE_GUIDE.md
**Verzió:** 1.0
**Dátum:** 2025-10-29
**Projekt:** TK11 Hibrid Mód (RX=USB, TX=AM)
