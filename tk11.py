#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TK11.exe patcher: Jcc -> NOP RVA-val vagy VA-val
------------------------------------------------
- Elfogad --rva és/vagy --va címeket. A --va esetén a script maga számolja az RVA-t: RVA = VA - ImageBase.
- A PE szekciótáblán keresztül fájl-offsetté alakítja a címeket, majd NOP-okra (0x90) írja a Jcc ugrásokat.
- Felismeri a rövid Jcc-t (0x70..0x7F → 2 bájt) és a near Jcc-t (0F 8x → 6 bájt), és ennek megfelelően NOP-ol.
- Kiírja az ImageBase-t és a szekciókat, hogy lásd, jó helyre célzol.

Használat (példák)
------------------
  # VA címekkel (x32dbg-ben látott abszolút címekkel):
  python tk11_nover_patch_v2.py TK11.exe --va 0x00534704 --va 0x00534714 -o TK11_nover.exe

  # RVA címekkel (ImageBase-től független offsetek):
  python tk11_nover_patch_v2.py TK11.exe --rva 0x00A4704 --rva 0x00A4714 -o TK11_nover.exe

Megjegyzés:
- A két fenti cím a „Version error” ághoz tartozó rövid ugrások tipikus címe (nálad eddig ezeket ütöttük ki).
- Ha találsz további ellenőrzéseket (pl. „File version is Wrong”, „Writing param” környékén),
  add hozzájuk a VA/RVA címeket további --va/--rva kapcsolókkal.
"""

import argparse, struct, sys
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Section:
    name: str
    va:   int   # VirtualAddress (RVA start)
    vsz:  int   # VirtualSize
    raw:  int   # PointerToRawData (file start)
    rsz:  int   # SizeOfRawData

def u16(b,o): return struct.unpack_from("<H", b, o)[0]
def u32(b,o): return struct.unpack_from("<I", b, o)[0]

def parse_pe(pe: bytes):
    if pe[:2] != b"MZ":
        raise ValueError("Not an MZ/PE file")
    e_lfanew = u32(pe, 0x3C)
    if pe[e_lfanew:e_lfanew+4] != b"PE\x00\x00":
        raise ValueError("Missing PE signature")
    coff = e_lfanew + 4
    nsec = u16(pe, coff + 2)
    opt  = coff + 20
    magic = u16(pe, opt + 0)
    if magic not in (0x10B, 0x20B):  # PE32 vagy PE32+
        raise ValueError(f"Unexpected OptionalHeader.Magic 0x{magic:X}")
    # ImageBase (PE32: 32-bit; PE32+: 64-bit -> itt 32-re olvassuk, TK11.exe várhatóan PE32)
    image_base = u32(pe, opt + (28 if magic == 0x10B else 24))
    size_opt = u16(pe, coff + 16)
    sec_off = opt + size_opt
    secs: List[Section] = []
    for i in range(nsec):
        off  = sec_off + i*40
        name = pe[off:off+8].split(b"\x00",1)[0].decode("ascii","ignore")
        vsz  = u32(pe, off + 8)
        va   = u32(pe, off + 12)
        rsz  = u32(pe, off + 16)
        raw  = u32(pe, off + 20)
        secs.append(Section(name, va, vsz, raw, rsz))
    return image_base, secs

def rva_to_off(sections: List[Section], rva: int) -> int:
    for s in sections:
        end = s.va + max(s.vsz, s.rsz)
        if s.va <= rva < end:
            return s.raw + (rva - s.va)
    raise ValueError(f"RVA 0x{rva:X} not inside any section")

def nop_jcc(buf: bytearray, off: int) -> int:
    """
    Rövid Jcc: 0x70..0x7F  -> NOP NOP (2 bájt)
    Near Jcc:  0F 8x ...... -> 6× NOP
    Ha nem tűnik Jcc-nek, óvatos default: 2 bájtot NOP-ol.
    Visszatér: hány bájtot NOP-olt.
    """
    if off+2 > len(buf):
        raise ValueError("Offset beyond EOF")
    b0 = buf[off]
    # short Jcc
    if 0x70 <= b0 <= 0x7F:
        buf[off:off+2] = b"\x90\x90"
        return 2
    # near Jcc (0F 8x)
    if b0 == 0x0F and off+6 <= len(buf) and 0x80 <= buf[off+1] <= 0x8F:
        buf[off:off+6] = b"\x90\x90\x90\x90\x90\x90"
        return 6
    # fallback
    buf[off:off+2] = b"\x90\x90"
    return 2

def main():
    ap = argparse.ArgumentParser(description="TK11.exe Jcc->NOP patcher (RVA/VA).")
    ap.add_argument("exe", help="Bemeneti EXE (pl. TK11.exe)")
    ap.add_argument("-o","--out", default="TK11_nover.exe", help="Kimeneti EXE")
    ap.add_argument("--rva", action="append", default=[], help="RVA (pl. 0x00A4704). Többször is megadható.")
    ap.add_argument("--va",  action="append", default=[], help="VA (pl. 0x00534704). Többször is megadható.")
    args = ap.parse_args()

    pe = bytearray(open(args.exe, "rb").read())
    image_base, sections = parse_pe(pe)

    print(f"[*] ImageBase: 0x{image_base:X}")
    print("[*] Sections:")
    for s in sections:
        print(f"    {s.name:8s}  RVA=0x{s.va:X}  VSZ=0x{s.vsz:X}  RAW=0x{s.raw:X}  RSZ=0x{s.rsz:X}  (end RVA=0x{s.va+max(s.vsz,s.rsz):X})")

    targets_rva: List[int] = []
    targets_rva += [int(x,0) for x in args.rva]
    targets_rva += [int(x,0) - image_base for x in args.va]

    if not targets_rva:
        print("[!] Adj meg legalább egy címet --va vagy --rva kapcsolóval.")
        sys.exit(2)

    print("[*] Targets (RVA):", ", ".join(f"0x{r:X}" for r in targets_rva))
    for r in targets_rva:
        off = rva_to_off(sections, r)
        n = nop_jcc(pe, off)
        print(f"    RVA 0x{r:X} @ file+0x{off:X}  -> NOP x{n}")

    open(args.out, "wb").write(pe)
    print(f"[+] Kész: {args.out}")

if __name__ == "__main__":
    main()
