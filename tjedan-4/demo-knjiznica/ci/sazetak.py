#!/usr/bin/env python3
"""Sažetak sigurnosnih testova po ranjivosti (K01–K08) iz JUnit XML (Maven Surefire, pytest) ili TRX (.NET).

  sazetak.py --ocekivano ranjivo  datoteke...   # svaka ranjivost mora imati barem jedan pali test
  sazetak.py --ocekivano rjesenje datoteke...   # svi testovi prolaze, a testovi postoje za svih 8 ranjivosti
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

K = re.compile(r"[Kk](0[1-8])")
SVE = [f"K{i:02d}" for i in range(1, 9)]


def rezultati(putanja):
    """Vraća popis (ranjivost, ime testa, prošao) iz jedne datoteke."""
    stablo = ET.parse(putanja)
    korijen = stablo.getroot()
    out = []
    if korijen.tag.endswith("TestRun"):  # TRX
        ns = {"t": korijen.tag.split("}")[0].strip("{")}
        for r in korijen.iterfind(".//t:UnitTestResult", ns):
            ime = r.get("testName", "")
            m = K.search(ime.split("(")[0])
            if m:
                out.append((f"K{m.group(1)}", ime, r.get("outcome") == "Passed"))
        return out
    for tc in korijen.iter("testcase"):
        ime = f"{tc.get('classname', '')}.{tc.get('name', '')}"
        m = K.search(tc.get("classname", "")) or K.search(tc.get("name", ""))
        if not m or tc.find("skipped") is not None:
            continue
        palo = tc.find("failure") is not None or tc.find("error") is not None
        out.append((f"K{m.group(1)}", ime, not palo))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ocekivano", choices=("ranjivo", "rjesenje"), required=True)
    ap.add_argument("--stack", default="")
    ap.add_argument("datoteke", nargs="+")
    a = ap.parse_args()
    po_k = defaultdict(lambda: [0, 0])  # [prošlo, palo]
    for d in a.datoteke:
        for k, _, prosao in rezultati(d):
            po_k[k][0 if prosao else 1] += 1
    redovi, greske = [], []
    for k in SVE:
        prosli, pali = po_k.get(k, [0, 0])
        if a.ocekivano == "ranjivo":
            stanje = "RANJIVO" if pali > 0 else "NIJE DOKAZANO"
            if pali == 0:
                greske.append(f"{k}: nijedan sigurnosni test ne pada na ranjivoj verziji")
        else:
            stanje = "ISPRAVLJENO" if pali == 0 and prosli > 0 else "GREŠKA"
            if pali or not prosli:
                greske.append(f"{k}: {pali} palih, {prosli} prošlih testova na rješenju")
        redovi.append(f"{k}: {stanje} ({pali}/{prosli + pali} testova pada)")
    naslov = f"{a.stack} – {a.ocekivano}"
    print(f"::notice title=Sažetak {naslov}::" + "%0A".join(redovi))
    print("\n".join(redovi))
    for g in greske:
        print(f"::error title={naslov}::{g}")
    sys.exit(1 if greske else 0)


if __name__ == "__main__":
    main()
