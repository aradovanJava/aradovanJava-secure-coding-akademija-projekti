#!/usr/bin/env python3
"""Provjera očekivanja za test DevSecOps predloška (čita izvjestaji/gate.json).

all-secure: vrata PROLAZE (dopušteni su samo prihvaćeni nalazi s obrazloženjem).
all-vuln:   vrata NE PROLAZE, uz stvarne blokirajuće nalaze iz SAST-a, SCA-a (ranjiva YAML
            biblioteka) i DAST-a; nijedan izvještaj ne smije nedostajati.
"""
import argparse
import json
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--stack", required=True)
ap.add_argument("--mode", required=True)
ap.add_argument("--gate", required=True)
a = ap.parse_args()

try:
    g = json.load(open(a.gate, encoding="utf-8"))
except OSError as e:
    print(f"::error title=t3-devsecops::Nema gate.json ({e})")
    sys.exit(1)

oznaka = f"{a.stack}/medtermin {a.mode}"
nalazi = g["nalazi"]
blok = [n for n in nalazi if n["status"] == "blokira"]
prih = [n for n in nalazi if n["status"] == "prihvaceno"]


def opis(n):
    lok = n["datoteka"] + (f":{n['redak']}" if n["redak"] else "")
    return f"{n['alat']}:{n['pravilo'].rsplit('.', 1)[-1]} @ {lok}"


for kat in ("sast", "sca", "tajne", "dast", "ci"):
    b = sorted({opis(n) for n in blok if n["kategorija"] == kat})
    p = sorted({opis(n) for n in prih if n["kategorija"] == kat})
    if b or p:
        print(f"::notice title={oznaka} {kat.upper()}::blokira {len(b)}: {'; '.join(b)[:900]}"
              + (f" | prihvaćeno {len(p)}: {'; '.join(p)[:300]}" if p else ""))

greske = []
if any(n["alat"] == "ci" for n in blok):
    greske.append("nedostaje izvještaj ili je alat pao: " + "; ".join(n["poruka"] for n in blok if n["alat"] == "ci"))
if a.mode == "all-secure":
    if not g["prolaz"]:
        greske.append("vrata moraju PROĆI na all-secure, a blokiraju: " + "; ".join(opis(n) for n in blok)[:1500])
    neobrazlozeni = [n for n in prih if not n.get("obrazlozenje")]
    if neobrazlozeni:
        greske.append("prihvaćeni nalazi bez obrazloženja")
else:
    if g["prolaz"]:
        greske.append("vrata moraju PASTI na all-vuln")
    if not [n for n in blok if n["kategorija"] == "sast"]:
        greske.append("SAST nema blokirajućih nalaza")
    yaml_lib = "snakeyaml" if a.stack == "java" else "yamldotnet"
    if not [n for n in blok if n["kategorija"] == "sca" and yaml_lib in n["datoteka"].lower()]:
        greske.append(f"SCA ne blokira ranjivu YAML biblioteku ({yaml_lib})")
    if not [n for n in blok if n["kategorija"] == "dast"]:
        greske.append("DAST (ZAP) nema blokirajućih nalaza")

for gr in greske:
    print(f"::error title={oznaka}::{gr}")
print(f"{oznaka}: prolaz={g['prolaz']}, blokira={len(blok)}, prihvaćeno={len(prih)}, "
      f"kategorije={json.dumps(g['kategorije'], ensure_ascii=False)}")
sys.exit(1 if greske else 0)
