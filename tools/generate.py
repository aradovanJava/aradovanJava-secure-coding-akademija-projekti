#!/usr/bin/env python3
"""Generator varijanti za Tjedan 2 (Secure Coding akademija).

Iz predložaka s markerima (// @@VULN Sxx … // @@SECURE Sxx … // @@END Sxx) stvara čisti projekt u kojem je
svako od 13 mjesta ranjivo ili sigurno, ovisno o varijanti.

Primjeri:
  generate.py --stack java   --domain medtermin --mode all-vuln   --dest /tmp/mt-vuln   --with-hidden
  generate.py --stack dotnet --domain ulaznica  --mode all-secure --dest /tmp/ul-sec    --with-hidden
  generate.py --stack java   --variant V07                         --dest /tmp/v07-java
  generate.py --student V07 --out dist/      # paket za polaznika: java/ + dotnet/ + upute + ZIP
"""
import argparse, json, os, re, shutil, stat, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOTS = [f"S{i:02d}" for i in range(1, 14)]
DOMAINS = {"medtermin": "MedTermin", "ulaznica": "Ulaznica", "kadrovska": "Kadrovska"}

TEXT_EXT = {".java", ".cs", ".xml", ".properties", ".yml", ".yaml", ".json", ".http", ".md", ".sql", ".txt",
            ".csproj", ".sln", ".props", ".targets", ".html", ".css", ".js", ".cmd", ".sh", ".editorconfig",
            ".gitignore", ".gitattributes", ".config", ".razor", ".cshtml"}
TEXT_NAMES = {"mvnw", "Dockerfile", ".editorconfig", ".gitignore", ".gitattributes"}
SKIP_DIRS = {"target", "bin", "obj", ".idea", ".vs", "TestResults", "node_modules", "data"}

MARK = re.compile(r"@@(VULN|SECURE|END)\s+(S\d\d)\b")
FILE_MARK = re.compile(r"@@FILE-(VULN|SECURE)\s+(S\d\d)\b")

# Riječi koje ne smiju biti u kodu koji vidi polaznik (otkrivale bi ranjivosti).
LINT_PATTERNS = [
    r"@@", r"\bS(0[1-9]|1[0-3])\b", r"ranjiv", r"nesigurn", r"vuln", r"insecure", r"exploit", r"napad",
    r"payload", r"injection", r"injekcij", r"\bXXE\b", r"\bIDOR\b", r"\bSSRF\b", r"CWE-", r"OWASP",
    r"traversal", r"race condition", r"fail-open", r"open redirect", r"skriven",
]
LINT_RE = re.compile("|".join(LINT_PATTERNS), re.IGNORECASE)
LINT_FILE_EXT = {".java", ".cs", ".xml", ".properties", ".json", ".http", ".csproj", ".sln", ".sql", ".html",
                 ".js", ".css", ".yml", ".yaml", ".md", ".cshtml", ".razor"}
LINT_SKIP_FILES = {"mvnw", "mvnw.cmd", "maven-wrapper.properties"}


class GenError(Exception):
    pass


def is_text(path):
    name = os.path.basename(path)
    return name in TEXT_NAMES or os.path.splitext(name)[1].lower() in TEXT_EXT


def process_text(text, vulnerable, origin):
    """Vrati obrađeni tekst ili None ako datoteku treba izostaviti."""
    lines = text.splitlines(keepends=True)
    if lines:
        fm = FILE_MARK.search(lines[0])
        if fm:
            kind, slot = fm.groups()
            if slot not in SLOTS:
                raise GenError(f"{origin}: nepoznat slot {slot}")
            keep = (kind == "VULN") == (slot in vulnerable)
            if not keep:
                return None
            lines = lines[1:]
    out, cur, branch, start = [], None, None, 0
    for no, line in enumerate(lines, 1):
        m = MARK.search(line)
        if m:
            kind, slot = m.groups()
            if slot not in SLOTS:
                raise GenError(f"{origin}:{no}: nepoznat slot {slot}")
            if kind == "VULN":
                if cur is not None:
                    raise GenError(f"{origin}:{no}: ugniježđeni marker ({cur} još otvoren)")
                cur, branch, start = slot, "VULN", no
            elif kind == "SECURE":
                if cur != slot or branch != "VULN":
                    raise GenError(f"{origin}:{no}: @@SECURE {slot} bez prethodnog @@VULN {slot}")
                branch = "SECURE"
            else:
                if cur != slot:
                    raise GenError(f"{origin}:{no}: @@END {slot} ne odgovara otvorenom bloku {cur}")
                cur, branch = None, None
            continue
        if "@@FILE-" in line:
            raise GenError(f"{origin}:{no}: @@FILE- marker smije biti samo u prvom retku")
        if cur is None:
            out.append(line)
        elif (branch == "VULN") == (cur in vulnerable):
            out.append(line)
    if cur is not None:
        raise GenError(f"{origin}:{start}: blok {cur} nije zatvoren s @@END")
    return "".join(out)


def read_text(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def write_text(path, text, bom):
    data = text.encode("utf-8")
    with open(path, "wb") as f:
        f.write((b"\xef\xbb\xbf" if bom else b"") + data)


def copy_tree(src, dest, vulnerable, process=True):
    count = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = os.path.relpath(root, src)
        for f in files:
            sp = os.path.join(root, f)
            dp = os.path.normpath(os.path.join(dest, rel, f))
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            if process and is_text(sp):
                text, bom = read_text(sp)
                res = process_text(text, vulnerable, os.path.relpath(sp, ROOT))
                if res is None:
                    continue
                write_text(dp, res, bom)
                shutil.copymode(sp, dp)
            else:
                shutil.copy2(sp, dp)
            count += 1
    return count


def lint(dest):
    problems = []
    for root, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and d not in {"docs", ".mvn"}]
        for f in files:
            if f in LINT_SKIP_FILES:
                continue
            p = os.path.join(root, f)
            if os.path.splitext(f)[1].lower() not in LINT_FILE_EXT:
                continue
            rel = os.path.relpath(p, dest)
            # skriveni testovi (kad su dodani) nisu dio studentskog koda
            if re.search(r"(^|[\\/])(skriveno|Skriveno)([\\/])", rel):
                continue
            try:
                text, _ = read_text(p)
            except UnicodeDecodeError:
                continue
            for no, line in enumerate(text.splitlines(), 1):
                m = LINT_RE.search(line)
                if m:
                    problems.append(f"{rel}:{no}: '{m.group(0)}' → {line.strip()[:120]}")
    return problems


def load_variants():
    with open(os.path.join(ROOT, "variants.json"), encoding="utf-8") as f:
        return json.load(f)


def hidden_target(stack, domain, dest):
    if stack == "java":
        return os.path.join(dest, "src", "test")
    return os.path.join(dest, "tests", f"{DOMAINS[domain]}.Tests")


def generate(stack, domain, vulnerable, dest, with_hidden=False, do_lint=True, quiet=False):
    src = os.path.join(ROOT, "templates", stack, domain)
    if not os.path.isdir(src):
        raise GenError(f"nema predloška {src}")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    n = copy_tree(src, dest, set(vulnerable))
    problems = lint(dest) if do_lint else []
    if with_hidden:
        hsrc = os.path.join(ROOT, "hidden-tests", stack, domain)
        if os.path.isdir(hsrc):
            n += copy_tree(hsrc, hidden_target(stack, domain, dest), set(vulnerable), process=True)
        elif not quiet:
            print(f"upozorenje: nema skrivenih testova u {hsrc}", file=sys.stderr)
    if not quiet:
        print(f"{stack}/{domain}: {n} datoteka → {dest} (ranjivo: {','.join(sorted(vulnerable)) or '-'})")
    if problems:
        msg = "\n".join(problems[:200])
        raise GenError(f"LINT: {len(problems)} problem(a) u generiranom kodu:\n{msg}")
    return dest


def render(template, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values.get(m.group(1), m.group(0))), template)


def student_package(variant, out_dir):
    variants = load_variants()
    if variant not in variants:
        raise GenError(f"nepoznata varijanta {variant}")
    v = variants[variant]
    domain, vulnerable = v["domain"], v["vulnerable"]
    name = f"projekt-{variant}-{domain}"
    base = os.path.join(out_dir, name)
    if os.path.exists(base):
        shutil.rmtree(base)
    os.makedirs(base)
    for stack in ("java", "dotnet"):
        if os.path.isdir(os.path.join(ROOT, "templates", stack, domain)):
            generate(stack, domain, vulnerable, os.path.join(base, stack), quiet=True)
    sd = os.path.join(ROOT, "student-docs")
    if os.path.isdir(sd):
        meta = json.load(open(os.path.join(sd, "domene.json"), encoding="utf-8"))[domain]
        values = dict(meta, VARIJANTA=variant, DOMENA=domain, DOMENA_KLASA=DOMAINS[domain])
        for root, dirs, files in os.walk(sd):
            for f in files:
                if f == "domene.json":
                    continue
                sp = os.path.join(root, f)
                rel = os.path.relpath(sp, sd)
                dp = os.path.join(base, rel)
                os.makedirs(os.path.dirname(dp), exist_ok=True)
                if is_text(sp):
                    text, bom = read_text(sp)
                    write_text(dp, render(text, values), bom)
                else:
                    shutil.copy2(sp, dp)
    zpath = os.path.join(out_dir, name + ".zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(base):
            for f in files:
                p = os.path.join(root, f)
                arc = os.path.relpath(p, out_dir)
                zi = zipfile.ZipInfo.from_file(p, arc)
                if f in ("mvnw",) or f.endswith(".sh"):
                    zi.external_attr = (0o755 | stat.S_IFREG) << 16
                with open(p, "rb") as fh:
                    z.writestr(zi, fh.read(), zipfile.ZIP_DEFLATED)
    print(f"{variant}: {zpath}")
    return zpath


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stack", choices=["java", "dotnet"])
    ap.add_argument("--domain", choices=list(DOMAINS))
    ap.add_argument("--mode", choices=["all-vuln", "all-secure", "variant"], default="variant")
    ap.add_argument("--variant")
    ap.add_argument("--dest")
    ap.add_argument("--with-hidden", action="store_true")
    ap.add_argument("--no-lint", action="store_true")
    ap.add_argument("--student", help="varijanta (npr. V07) ili 'all' – izradi paket(e) za polaznike")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    ap.add_argument("--print-vulnerable", action="store_true", help="samo ispiši ranjive slotove varijante")
    a = ap.parse_args()
    try:
        if a.student:
            os.makedirs(a.out, exist_ok=True)
            names = sorted(load_variants()) if a.student == "all" else [a.student]
            for n in names:
                student_package(n, a.out)
            return
        if a.variant:
            v = load_variants()[a.variant]
            domain, vulnerable = v["domain"], v["vulnerable"]
            if a.print_vulnerable:
                print(",".join(vulnerable)); return
        else:
            if not a.domain:
                ap.error("--domain ili --variant je obavezan")
            domain = a.domain
            vulnerable = SLOTS if a.mode == "all-vuln" else [] if a.mode == "all-secure" else ap.error("--mode")
        if not a.stack or not a.dest:
            ap.error("--stack i --dest su obavezni")
        generate(a.stack, domain, vulnerable, a.dest, a.with_hidden, not a.no_lint)
    except GenError as e:
        print(f"GREŠKA: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
