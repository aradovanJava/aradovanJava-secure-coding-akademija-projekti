#!/usr/bin/env python3
"""Sažetak nalaza alata nad ranjivom verzijom (za vodič predavača): Semgrep, SpotBugs, OSV-Scanner, ZAP, Bandit."""
import json
import os
import sys
import xml.etree.ElementTree as ET


def semgrep(p):
    d = json.load(open(p))
    for r in d.get("results", []):
        yield f"SEMGREP {r['check_id'].split('.')[-1]} {r['path']}:{r['start']['line']}"


def spotbugs(p):
    for b in ET.parse(p).getroot().iter("BugInstance"):
        src = b.find("SourceLine")
        mjesto = f"{src.get('sourcepath')}:{src.get('start')}" if src is not None else ""
        yield f"SPOTBUGS {b.get('type')} ({b.get('category')}, rang {b.get('rank')}) {mjesto}"


def osv(p):
    d = json.load(open(p))
    for rez in d.get("results", []):
        for pkg in rez.get("packages", []):
            ime = f"{pkg['package']['name']} {pkg['package'].get('version', '')}"
            ids = sorted({v["id"] for v in pkg.get("vulnerabilities", [])})
            yield f"OSV {ime}: {', '.join(ids)}"


def zap(p):
    d = json.load(open(p))
    for site in d.get("site", []):
        for a in site.get("alerts", []):
            yield f"ZAP [{a.get('riskdesc')}] {a.get('alert')} (pluginid {a.get('pluginid')})"


def bandit(p):
    d = json.load(open(p))
    for r in d.get("results", []):
        yield f"BANDIT {r['test_id']} {r['test_name']} {r['filename']}:{r['line_number']} ({r['issue_severity']})"


VRSTE = {"semgrep": semgrep, "spotbugs": spotbugs, "osv": osv, "zap": zap, "bandit": bandit}


def main():
    stack = sys.argv[1]
    redovi = []
    for arg in sys.argv[2:]:
        vrsta, putanja = arg.split("=", 1)
        if not os.path.exists(putanja):
            redovi.append(f"{vrsta.upper()}: nema izvještaja ({putanja})")
            continue
        try:
            redovi.extend(VRSTE[vrsta](putanja))
        except Exception as e:  # noqa: BLE001
            redovi.append(f"{vrsta.upper()}: izvještaj nije čitljiv ({e})")
    print("\n".join(redovi))
    for i in range(0, len(redovi), 25):
        print(f"::notice title=Alati {stack} ({i // 25 + 1})::" + "%0A".join(redovi[i:i + 25]))


if __name__ == "__main__":
    main()
