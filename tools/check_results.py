#!/usr/bin/env python3
"""Čita rezultate testova (JUnit XML iz Surefirea ili .NET TRX) i uspoređuje ih s očekivanim stanjem varijante.

  check_results.py --results <dir> --expect-vulnerable S01,S02,...   [--gha] [--json out.json] [--label txt]
  check_results.py --results <dir> --summary-only                    (za ocjenjivanje: samo sažetak)

Pravila (kad se zadaje očekivanje):
  - funkcionalni i primjer testovi moraju proći,
  - za svaki RANJIVI slot barem jedan skriveni test PADA,
  - za svaki SIGURNI slot svi skriveni testovi PROLAZE,
  - svaki slot S01–S13 ima barem jedan skriveni test.
"""
import argparse, glob, json, os, re, sys
import xml.etree.ElementTree as ET

SLOTS = [f"S{i:02d}" for i in range(1, 14)]


def classify(classname, name):
    full = f"{classname}.{name}"
    low = full.lower()
    if ".skriveno." in low:
        simple = classname.split(".")[-1]
        # Java/.NET: klasa S01…Test(s); Python: modul test_s01_….py
        m = re.match(r"(?:test_?)?[Ss](\d\d)", simple)
        return ("skriveno", f"S{m.group(1)}" if m else None)
    if ".funkcionalno." in low:
        return ("funkcionalno", None)
    if ".primjer." in low:
        return ("primjer", None)
    return ("polaznik", None)


def parse_junit(path):
    out = []
    root = ET.parse(path).getroot()
    for tc in root.iter("testcase"):
        cls = tc.get("classname", "")
        name = tc.get("name", "")
        status = "pass"
        if tc.find("failure") is not None or tc.find("error") is not None:
            status = "fail"
        elif tc.find("skipped") is not None:
            status = "skip"
        out.append((cls, name, status))
    return out


def parse_trx(path):
    ns = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
    root = ET.parse(path).getroot()
    defs = {}
    for ut in root.iterfind(".//t:TestDefinitions/t:UnitTest", ns):
        tm = ut.find("t:TestMethod", ns)
        defs[ut.get("id")] = (tm.get("className", ""), tm.get("name", ""))
    out = []
    for r in root.iterfind(".//t:Results/t:UnitTestResult", ns):
        cls, name = defs.get(r.get("testId"), ("", r.get("testName", "")))
        cls = cls.split(",")[0]
        outcome = r.get("outcome", "")
        status = "pass" if outcome == "Passed" else "skip" if outcome in ("NotExecuted", "Inconclusive") else "fail"
        out.append((cls, name, status))
    return out


def collect(results_dir):
    tests = []
    for p in glob.glob(os.path.join(results_dir, "**", "TEST-*.xml"), recursive=True):
        tests += parse_junit(p)
    for p in glob.glob(os.path.join(results_dir, "**", "*.trx"), recursive=True):
        tests += parse_trx(p)
    return tests


def summarize(tests):
    s = {"slots": {k: {"pass": 0, "fail": 0, "tests": []} for k in SLOTS},
         "funkcionalno": {"pass": 0, "fail": 0, "failed": []},
         "primjer": {"pass": 0, "fail": 0, "failed": []},
         "polaznik": {"pass": 0, "fail": 0, "failed": [], "tests": []},
         "ukupno": len(tests)}
    for cls, name, status in tests:
        kind, slot = classify(cls, name)
        if status == "skip":
            continue
        if kind == "skriveno":
            if slot in s["slots"]:
                s["slots"][slot]["pass" if status == "pass" else "fail"] += 1
                s["slots"][slot]["tests"].append({"test": f"{cls.split('.')[-1]}.{name}", "status": status})
        else:
            b = s[kind]
            b["pass" if status == "pass" else "fail"] += 1
            if status != "pass":
                b["failed"].append(f"{cls.split('.')[-1]}.{name}")
            if kind == "polaznik":
                b["tests"].append({"test": f"{cls.split('.')[-1]}.{name}", "status": status})
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--expect-vulnerable", default=None, help="zarezom odvojeni slotovi koji su ranjivi")
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--gha", action="store_true", help="ispiši ::notice/::error anotacije")
    ap.add_argument("--json")
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    tests = collect(a.results)
    s = summarize(tests)
    if a.json:
        json.dump(s, open(a.json, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    if not tests:
        print(f"{'::error::' if a.gha else ''}{a.label} Nema rezultata testova u {a.results} (build nije uspio?)")
        sys.exit(1)

    errors, lines = [], []
    vuln = None if a.expect_vulnerable is None else {x for x in a.expect_vulnerable.split(",") if x}
    for slot in SLOTS:
        d = s["slots"][slot]
        tot = d["pass"] + d["fail"]
        state = "—" if tot == 0 else ("PADA" if d["fail"] else "PROLAZI")
        exp = ""
        if vuln is not None:
            exp = " (očekivano: ranjivo)" if slot in vuln else " (očekivano: sigurno)"
            if tot == 0:
                errors.append(f"{slot}: nema skrivenih testova")
            elif slot in vuln and d["fail"] == 0:
                errors.append(f"{slot}: ranjivo, ali svi skriveni testovi prolaze ({d['pass']}/{tot})")
            elif slot not in vuln and d["fail"] > 0:
                failed = [t["test"] for t in d["tests"] if t["status"] != "pass"]
                errors.append(f"{slot}: sigurno, ali pada {d['fail']}/{tot}: {', '.join(failed)}")
        lines.append(f"{slot}: {state} (pada {d['fail']}/{tot}){exp}")
    for kind in ("funkcionalno", "primjer"):
        b = s[kind]
        lines.append(f"{kind}: prolazi {b['pass']}/{b['pass'] + b['fail']}")
        if vuln is not None and b["fail"]:
            errors.append(f"{kind} testovi padaju: {', '.join(b['failed'][:10])}")
    if s["polaznik"]["pass"] + s["polaznik"]["fail"]:
        lines.append(f"ostali testovi: prolazi {s['polaznik']['pass']}/{s['polaznik']['pass'] + s['polaznik']['fail']}")

    head = f"{a.label} " if a.label else ""
    if a.gha:
        print(f"::notice title={head or 'Rezultati'}::" + " | ".join(lines))
        for e in errors:
            print(f"::error title={head or 'Odstupanje'}::{e}")
    print(head + "\n  " + "\n  ".join(lines))
    if errors:
        print("ODSTUPANJA:\n  " + "\n  ".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
