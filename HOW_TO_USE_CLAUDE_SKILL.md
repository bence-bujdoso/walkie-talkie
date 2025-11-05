# TK-11 Claude Code Skill - Használati útmutató

## Mi ez?

Létrehoztam egy Claude Code "skill"-t, ami specializálódott a TK-11 rádió firmware reverse engineering feladataira.

## Telepítés

A skill már telepítve van a projektben:
```
E:\AI\tk11\.claude\skills\radio-firmware-analyzer.md
```

## Használat Claude Code-ban

### 1. Indítsd el Claude Code-ot a tk11 mappában

```bash
cd E:\AI\tk11
claude
```

vagy nyisd meg a tk11 mappát Visual Studio Code-ban Claude Code extension-nel.

### 2. Aktiváld a skill-t

A skill automatikusan elérhető lesz, mivel a `.claude/skills/` mappában van.

Ha használni szeretnéd, egyszerűen írj egy parancsot, ami a skill területéhez tartozik:

```
Analyze the TK11 firmware
```

```
Find USB mode patterns in the .dat file
```

```
Create a script to enable TX on all modes
```

```
Patch TK11.exe to remove version check
```

### 3. Mit tud a skill?

A skill a következő területeken segít:

#### A) Firmware analízis
- Binary fájl (.bin) elemzés
- String kivonás
- Modulációs mód pattern keresés
- Channel struktúra azonosítás
- TX/RX flag keresés

#### B) Konfigurációs fájl módosítás
- .dat fájl elemzés
- Csatorna mód változtatás
- TX enable flag beállítás
- Frekvencia módosítás

#### C) PE file patching
- TK11.exe struktúra parse-olás
- Version check bypass
- Conditional jump NOP-olás
- RVA → file offset számítás

#### D) Python script generálás
- Firmware analyzer
- Byte patcher
- Checksum calculator
- Configuration modifier

## Példa használat

### Példa 1: Firmware elemzés

```
You: Analyze TK11_v5.00.09_ENG.bin and find USB mode references

Claude: [Runs firmware_analyzer.py or creates analysis script]
        [Shows results with hex offsets]
        [Explains findings]
```

### Példa 2: Mode patch létrehozás

```
You: Create a Python script to change channel 38 from FM to USB mode

Claude: [Generates script with proper offset calculation]
        [Shows hex dump before/after]
        [Explains modulation change]
```

### Példa 3: TK11.exe patching

```
You: How can I patch TK11.exe to skip the version check?

Claude: [Explains PE structure]
        [Shows how to find version check code]
        [Provides NOP patching instructions]
        [Can generate automated patch script]
```

## Előnyök

1. **Kontextus**: A skill ismeri a TK-11 projekt struktúráját
2. **Szakértelem**: Radio firmware reverse engineering specifikus tudás
3. **Gyorsaság**: Nem kell minden alkalommal elmagyarázni a projektet
4. **Konzisztencia**: Következetes válaszok és script formátumok
5. **Best practices**: Automatikusan követi a biztonságos patching gyakorlatokat

## Skill frissítés

Ha módosítani szeretnéd a skill-t:

1. Szerkeszd: `E:\AI\tk11\.claude\skills\radio-firmware-analyzer.md`
2. Add hozzá az új tudást vagy példákat
3. Mentés után a következő Claude Code session-ben már érvényes lesz

## Tippek

- A skill mindig elérhető, ha a tk11 mappában vagy
- Használd természetes nyelvű parancsokat
- A skill automatikusan Python script-eket generál, ha szükséges
- Minden patch előtt backup-ot készít
- Hex offset-eket mindig részletesen dokumentálja

## Hibaelhárítás

Ha a skill nem működik:
- Ellenőrizd, hogy létezik-e: `E:\AI\tk11\.claude\skills\radio-firmware-analyzer.md`
- Indítsd újra Claude Code-ot
- Győződj meg róla, hogy a tk11 mappában vagy

---

## Példa Session

```bash
$ cd E:\AI\tk11
$ claude

You: Use the radio firmware analyzer skill to check TK11.dat for USB modes

Claude: I'll analyze the TK11.dat configuration file for USB mode entries...
        [Runs analysis]

        Found USB mode (0x02) at:
        - Offset 0x1A4: Channel 38 (K38) - RX=USB, TX=DISABLED
        - Offset 0x2C8: Channel 40 (K40) - RX=USB, TX=DISABLED

        To enable TX, we need to change byte at offset:
        - 0x1A8: 0x00 → 0x01 (K38 TX enable)

        Would you like me to create a patch script?

You: Yes, create it

Claude: [Creates modify_k38_tx.py script]
        [Shows code]
        [Explains usage]
```

---

73! 📻

Enjoy your TK-11 firmware hacking with AI assistance!
