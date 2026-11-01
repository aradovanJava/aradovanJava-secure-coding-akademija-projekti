#!/usr/bin/env python3
"""Ocjenjivanje predaje polaznika (Tjedan 2) skrivenim testovima.

  python3 tools/ocijeni.py --predaja predaje/V07-Ime-Prezime.zip [--variant V07] [--stack auto|java|dotnet]
                           [--out izvjestaji/V07-Ime-Prezime.md]

Što radi:
  1. raspakira predaju i pronađe projekt (pom.xml → Java, *.sln → .NET; ako su oba, uzima onaj koji je mijenjan),
  2. u kopiju predaje doda skrivene testove i pokrene SVE testove → koji su ranjivi slotovi ispravljeni,
     jesu li sigurni slotovi ostali sigurni, prolaze li funkcionalni testovi, pokrivenost koda,
  3. testove polaznika pokrene na IZVORNOJ varijanti → koji testovi „hvataju” ranjivost (crveno → zeleno),
  4. ispiše izvještaj (Markdown) s prijedlogom razina prema rubrici iz programa.

Potrebno lokalno: Python 3.9+, JDK 21 (za Java predaje) i/ili .NET 10 SDK (za .NET predaje).
Isto se može pokrenuti u GitHub Actions (workflow „ocijeni”).
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import generate as gen            # noqa: E402
import check_results as chk       # noqa: E402

SLOT_NAMES = {
    "S01": ("A01", "IDOR kod brisanja tuđeg zapisa"),
    "S02": ("A01", "Path traversal kod preuzimanja datoteke"),
    "S03": ("A01", "Open redirect nakon prijave"),
    "S04": ("A02", "CORS prihvaća bilo koji origin uz credentials"),
    "S05": ("A02", "XXE kod uvoza XML-a"),
    "S06": ("A03", "Ranjiva biblioteka za YAML"),
    "S07": ("A04", "Lozinke kao SHA-256 bez soli"),
    "S08": ("A05", "SQL injection u parametru sortiranja"),
    "S09": ("A05", "Pohranjeni XSS na stranici za ispis"),
    "S10": ("A06", "Utrka kod zadnjeg slobodnog mjesta"),
    "S11": ("A07", "Predvidljiv/višekratni token za reset lozinke"),
    "S12": ("A09", "Osjetljivi podaci u logu, nema zapisa neuspjele prijave"),
    "S13": ("A10", "Fail-open kod iznimke u provjeri pristupa"),
}
IS_WIN = os.name == "nt"


def find_projects(base):
    found = {}
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in gen.SKIP_DIRS and not d.startswith(".")]
        depth = root.count(os.sep)
        if "pom.xml" in files and ("java" not in found or depth < found["java"][1]):
            found["java"] = (root, depth)
        if any(f.endswith(".sln") or f.endswith(".slnx") for f in files) and ("dotnet" not in found or depth < found["dotnet"][1]):
            found["dotnet"] = (root, depth)
    return {k: v[0] for k, v in found.items()}


def clean_copy(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*gen.SKIP_DIRS, ".git"))


def run(cmd, cwd, log):
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(f"\n$ {' '.join(cmd)}\n")
        fh.flush()
        return subprocess.call(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, shell=IS_WIN)


def run_tests(stack, proj, res):
    """Vrati (build_ok, coverage_percent)."""
    os.makedirs(res, exist_ok=True)
    log = os.path.join(res, "build.log")
    if stack == "java":
        mvnw = os.path.join(proj, "mvnw.cmd" if IS_WIN else "mvnw")
        if not IS_WIN and os.path.exists(mvnw):
            os.chmod(mvnw, 0o755)
        cmd = [mvnw if os.path.exists(mvnw) else "mvn", "-B", "-ntp", "test", "-Dmaven.test.failure.ignore=true"]
        rc = run(cmd, proj, log)
        sr = os.path.join(proj, "target", "surefire-reports")
        if os.path.isdir(sr):
            shutil.copytree(sr, os.path.join(res, "surefire-reports"), dirs_exist_ok=True)
        cov = None
        jx = os.path.join(proj, "target", "site", "jacoco", "jacoco.xml")
        if os.path.exists(jx):
            r = ET.parse(jx).getroot()
            for c in r.findall("counter"):
                if c.get("type") == "LINE":
                    m, cv = int(c.get("missed")), int(c.get("covered"))
                    cov = 100.0 * cv / max(1, m + cv)
        return rc == 0, cov
    sln = sorted(glob.glob(os.path.join(proj, "*.sln")) + glob.glob(os.path.join(proj, "*.slnx")))[0]
    if run(["dotnet", "build", sln, "-c", "Debug", "-nologo"], proj, log) != 0:
        return False, None
    run(["dotnet", "test", sln, "--no-build", "-nologo", "--logger", "trx;LogFileName=rezultati.trx",
         "--results-directory", res, "--collect:XPlat Code Coverage"], proj, log)
    cov = None
    for cx in glob.glob(os.path.join(res, "**", "coverage.cobertura.xml"), recursive=True):
        r = ET.parse(cx).getroot()
        try:
            cov = 100.0 * float(r.get("line-rate", "0"))
        except ValueError:
            pass
    return bool(glob.glob(os.path.join(res, "*.trx"))), cov


def student_test_files(stack, proj, domain):
    """Datoteke s testovima polaznika (bez funkcionalnih, primjera i skrivenih)."""
    out = []
    if stack == "java":
        base = os.path.join(proj, "src", "test")
        for p in glob.glob(os.path.join(base, "**", "*"), recursive=True):
            rel = os.path.relpath(p, proj).replace("\\", "/")
            if os.path.isfile(p) and not re.search(r"/(funkcionalno|primjer|skriveno)/", rel):
                out.append(rel)
    else:
        tdir = os.path.join(proj, "tests", f"{gen.DOMAINS[domain]}.Tests")
        for p in glob.glob(os.path.join(tdir, "**", "*.cs"), recursive=True):
            rel = os.path.relpath(p, proj).replace("\\", "/")
            if not re.search(r"/(Funkcionalno|Primjer|Skriveno|bin|obj)/", rel):
                out.append(rel)
    return out


def changed_files(stack, domain, vulnerable, proj, work):
    orig = os.path.join(work, f"cmp-{stack}")
    gen.generate(stack, domain, vulnerable, orig, quiet=True, do_lint=False)
    n = 0
    for root, dirs, files in os.walk(proj):
        dirs[:] = [d for d in dirs if d not in gen.SKIP_DIRS]
        for f in files:
            p = os.path.join(root, f)
            q = os.path.join(orig, os.path.relpath(p, proj))
            if not os.path.exists(q) or open(p, "rb").read() != open(q, "rb").read():
                n += 1
    return n


def level(pct, thresholds):
    for name, t in zip(("izvrstan", "vrlo dobar", "dobar", "dovoljan"), thresholds):
        if pct >= t:
            return name
    return "nedovoljno"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--predaja", required=True, help="ZIP ili mapa s predajom")
    ap.add_argument("--variant")
    ap.add_argument("--stack", default="auto", choices=["auto", "java", "dotnet"])
    ap.add_argument("--out")
    ap.add_argument("--keep", action="store_true", help="ne briši privremene mape")
    a = ap.parse_args()

    work = tempfile.mkdtemp(prefix="ocjena-")
    src = a.predaja
    if zipfile.is_zipfile(src):
        ex = os.path.join(work, "predaja")
        with zipfile.ZipFile(src) as z:
            for m in z.namelist():                     # zaštita od „zip slip” putanja
                t = os.path.realpath(os.path.join(ex, m))
                if not t.startswith(os.path.realpath(ex) + os.sep) and t != os.path.realpath(ex):
                    sys.exit(f"Neispravna putanja u ZIP-u: {m}")
            z.extractall(ex)
        src = ex
    variant = a.variant
    if not variant:
        m = re.search(r"(V\d\d)", os.path.basename(a.predaja))
        if not m:
            for p in glob.glob(os.path.join(src, "**", "README.md"), recursive=True):
                m = re.search(r"Varijanta\s+\**(V\d\d)", open(p, encoding="utf-8", errors="ignore").read())
                if m:
                    break
        if not m:
            sys.exit("Ne mogu odrediti varijantu – zadaj --variant Vxx")
        variant = m.group(1)
    v = gen.load_variants()[variant]
    domain, vulnerable = v["domain"], v["vulnerable"]

    projects = find_projects(src)
    if a.stack != "auto":
        if a.stack not in projects:
            sys.exit(f"U predaji nema {a.stack} projekta.")
        stack = a.stack
    elif len(projects) == 1:
        stack = next(iter(projects))
    elif projects:
        scores = {s: changed_files(s, domain, vulnerable, p, work) for s, p in projects.items()}
        stack = max(scores, key=scores.get)
        print(f"Predaja sadrži oba projekta; promijenjenih datoteka: {scores} → ocjenjujem {stack}")
    else:
        sys.exit("U predaji nema Maven (pom.xml) ni .NET (.sln) projekta.")
    proj_src = projects[stack]
    print(f"Varijanta {variant} ({domain}), {stack}: {proj_src}")

    # 1) predaja + skriveni testovi
    fixed = os.path.join(work, "ispravljeno")
    clean_copy(proj_src, fixed)
    hsrc = os.path.join(ROOT, "hidden-tests", stack, domain)
    gen.copy_tree(hsrc, gen.hidden_target(stack, domain, fixed), set(vulnerable))
    res_fixed = os.path.join(work, "rez-ispravljeno")
    build_ok, coverage = run_tests(stack, fixed, res_fixed)
    s = chk.summarize(chk.collect(res_fixed)) if build_ok else None

    # 2) testovi polaznika na izvornoj varijanti
    stud_files = student_test_files(stack, proj_src, domain)
    red = {}
    orig_note = ""
    if stud_files:
        orig = os.path.join(work, "izvorno")
        gen.generate(stack, domain, vulnerable, orig, quiet=True, do_lint=False)
        for rel in stud_files:
            d = os.path.join(orig, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(os.path.join(proj_src, rel), d)
        res_orig = os.path.join(work, "rez-izvorno")
        ok, _ = run_tests(stack, orig, res_orig)
        if ok:
            so = chk.summarize(chk.collect(res_orig))
            for t in so["polaznik"]["tests"]:
                red[t["test"]] = t["status"]
        else:
            orig_note = ("Testovi polaznika ne mogu se prevesti nad izvornim kodom (vjerojatno koriste klase "
                         "dodane u popravku) – crveno→zeleno provjeri ručno.")

    # 3) izvještaj
    L = [f"# Ocjena projekta – varijanta {variant} ({domain}, {stack})", "",
         f"Predaja: `{os.path.basename(a.predaja)}`", ""]
    if not build_ok:
        L += ["**Build predaje (s dodanim skrivenim testovima) nije uspio.** Pogledaj `build.log`:", "",
              "```", open(os.path.join(res_fixed, "build.log"), encoding="utf-8", errors="ignore").read()[-3000:], "```"]
    else:
        fixed_n = 0
        L += ["## Ranjivosti u varijanti", "", "| Slot | OWASP | Ranjivost | Skriveni testovi | Stanje |", "|---|---|---|---|---|"]
        for slot in vulnerable:
            d = s["slots"][slot]
            tot = d["pass"] + d["fail"]
            ok = tot > 0 and d["fail"] == 0
            fixed_n += ok
            L.append(f"| {slot} | {SLOT_NAMES[slot][0]} | {SLOT_NAMES[slot][1]} | {d['pass']}/{tot} | "
                     f"{'ISPRAVLJENO' if ok else 'NIJE ISPRAVLJENO'} |")
        regress = [sl for sl in chk.SLOTS if sl not in vulnerable and s["slots"][sl]["fail"]]
        L += ["", f"**Ispravljeno: {fixed_n}/{len(vulnerable)}**"]
        if regress:
            L.append(f"\n⚠️ Uvedene nove ranjivosti / regresije u slotovima: {', '.join(regress)}")
        f = s["funkcionalno"]
        L += ["", f"Funkcionalni testovi: {f['pass']}/{f['pass'] + f['fail']} prolazi"
              + (f" – padaju: {', '.join(f['failed'])} (popravak je slomio funkcionalnost?)" if f["fail"] else "")]
        st = s["polaznik"]["tests"]
        rg = [t for t in st if t["status"] == "pass" and red.get(t["test"]) == "fail"]
        L += ["", "## Testovi polaznika", "",
              f"Testova polaznika: {len(st)}; prolaze na predaji: {sum(t['status'] == 'pass' for t in st)}; "
              f"padaju na izvornom kodu i prolaze na predaji (crveno → zeleno): **{len(rg)}**"]
        if orig_note:
            L.append(f"\n{orig_note}")
        if st:
            L += ["", "| Test | Predaja | Izvorni kod |", "|---|---|---|"]
            for t in st:
                L.append(f"| `{t['test']}` | {t['status']} | {red.get(t['test'], '—')} |")
        cov_txt = f"{coverage:.1f} %" if coverage is not None else "nije dostupno"
        L += ["", f"Pokrivenost koda (linije): **{cov_txt}**"]
        pct_fixed = 100.0 * fixed_n / len(vulnerable)
        pct_tests = 100.0 * min(len(rg), fixed_n) / max(1, fixed_n)
        L += ["", "## Prijedlog prema rubrici iz programa (nastavnik korigira)", "",
              "| Element | Mjera | Prijedlog |", "|---|---|---|",
              f"| Pronalaženje i ispravljanje ranjivosti alatima | {fixed_n}/{len(vulnerable)} ispravljeno | "
              f"{'izvrstan' if fixed_n == len(vulnerable) else 'vrlo dobar' if fixed_n >= 8 else 'dobar' if fixed_n == 7 else 'dovoljan' if fixed_n == 6 else 'nedovoljno'} "
              f"(spusti razinu ako su korišteni savjeti: razina 1 = „uz povremenu pomoć”, razina 2 = „uz stalnu pomoć”) |",
              f"| Pokrivanje ranjivosti jediničnim testovima | ~{pct_tests:.0f} % ispravljenih ima test crveno→zeleno | "
              f"{level(pct_tests, (100, 80, 60, 40))} (provjeri ručno da testovi ciljaju ranjivosti) |",
              f"| Pokrivenost koda jediničnim testovima | {cov_txt} | "
              f"{level(coverage or 0, (80, 60, 40, 20)) if coverage is not None else '—'} |",
              "| Usklađenost sa standardima (ASVS, model prijetnji) | izvještaj | ocijeni ručno |"]
    report = "\n".join(L) + "\n"
    out = a.out or os.path.join(ROOT, "izvjestaji", f"{variant}-{os.path.splitext(os.path.basename(a.predaja))[0]}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(report)
    print(report)
    print(f"Izvještaj: {out}")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8").write(report)
    if not a.keep:
        shutil.rmtree(work, ignore_errors=True)
    else:
        print(f"Privremene mape: {work}")


if __name__ == "__main__":
    main()
