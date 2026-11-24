#!/usr/bin/env python3
"""Generator demo aplikacije Knjižnica (Tjedan 4, demonstracija predavača).

Iz predložaka s oznakama (@@VULN Kxx … @@SECURE Kxx … @@END Kxx) stvara:
  - ranjivu verziju (polazište demonstracije) – bez sigurnosnih testova ili s njima,
  - referentno rješenje – sve ranjivosti ispravljene, sa sigurnosnim testovima.

Primjeri:
  generiraj.py --stack python --mode ranjivo   --dest /tmp/knj-py
  generiraj.py --stack java   --mode ranjivo   --s-testovima --dest /tmp/knj-java-test
  generiraj.py --stack dotnet --mode rjesenje  --dest /tmp/knj-net-rj
  generiraj.py --paket dist/     # ZIP za polaznike (ranjivo, sva tri stacka, bez sigurnosnih testova)
"""
import argparse
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PREDLOZAK = os.path.join(ROOT, "predlozak")
SLOTS = [f"K{i:02d}" for i in range(1, 9)]
STACKS = ("java", "dotnet", "python")
MARK = re.compile(r"@@(VULN|SECURE|END)\s+(K\d\d)\b")
FILE_MARK = re.compile(r"@@FILE-(VULN|SECURE)\s+(K\d\d)\b")
SKIP_DIRS = {"target", "bin", "obj", ".idea", ".vs", "TestResults", "__pycache__", ".pytest_cache",
             ".venv", "venv", ".ruff_cache", "htmlcov"}
TEXT_EXT = {".java", ".cs", ".py", ".xml", ".properties", ".json", ".http", ".md", ".sql", ".txt", ".toml",
            ".csproj", ".sln", ".yml", ".yaml", ".cmd", ".sh", ".editorconfig", ".gitignore", ".cfg", ".ini"}
TEXT_NAMES = {"mvnw", ".editorconfig", ".gitignore", ".gitattributes"}
# U ranjivoj verziji ne smije biti riječi koje otkrivaju gdje su ranjivosti.
LINT = re.compile(r"@@|\bK0[1-8]\b|ranjiv|nesigurn|vuln|insecure|exploit|napad|payload|injection|injekcij"
                  r"|\bIDOR\b|CWE-|OWASP|fail-open", re.IGNORECASE)


class GenError(Exception):
    pass


def process(text, keep_secure, origin):
    lines = text.splitlines(keepends=True)
    if lines:
        fm = FILE_MARK.search(lines[0])
        if fm:
            kind, slot = fm.groups()
            if slot not in SLOTS:
                raise GenError(f"{origin}: nepoznata oznaka {slot}")
            if (kind == "SECURE") != keep_secure:
                return None
            lines = lines[1:]
    out, cur, branch, start = [], None, None, 0
    for no, line in enumerate(lines, 1):
        m = MARK.search(line)
        if m:
            kind, slot = m.groups()
            if slot not in SLOTS:
                raise GenError(f"{origin}:{no}: nepoznata oznaka {slot}")
            if kind == "VULN":
                if cur is not None:
                    raise GenError(f"{origin}:{no}: ugniježđena oznaka ({cur} je otvorena)")
                cur, branch, start = slot, "VULN", no
            elif kind == "SECURE":
                if cur != slot or branch != "VULN":
                    raise GenError(f"{origin}:{no}: @@SECURE {slot} bez @@VULN {slot}")
                branch = "SECURE"
            else:
                if cur != slot or branch != "SECURE":
                    raise GenError(f"{origin}:{no}: @@END {slot} ne zatvara otvoreni blok")
                cur = branch = None
            continue
        if "@@FILE-" in line:
            raise GenError(f"{origin}:{no}: @@FILE- smije biti samo u prvom retku")
        if cur is None or (branch == "SECURE") == keep_secure:
            out.append(line)
    if cur is not None:
        raise GenError(f"{origin}:{start}: blok {cur} nije zatvoren")
    return "".join(out)


def is_text(path):
    name = os.path.basename(path)
    return name in TEXT_NAMES or os.path.splitext(name)[1].lower() in TEXT_EXT


def copy_tree(src, dest, keep_secure):
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        rel = os.path.relpath(dirpath, src)
        for name in sorted(filenames):
            s = os.path.join(dirpath, name)
            d = os.path.normpath(os.path.join(dest, rel, name))
            if is_text(s):
                with open(s, "rb") as f:
                    raw = f.read()
                bom = raw.startswith(b"\xef\xbb\xbf")
                text = raw.decode("utf-8-sig")
                result = process(text, keep_secure, os.path.relpath(s, ROOT))
                if result is None:
                    continue
                os.makedirs(os.path.dirname(d), exist_ok=True)
                with open(d, "wb") as f:
                    f.write((b"\xef\xbb\xbf" if bom else b"") + result.encode("utf-8"))
            else:
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(s, d)
            if name in ("mvnw", "run.py") or name.endswith(".sh"):
                os.chmod(d, 0o755)


def lint(dest):
    problemi = []
    for dirpath, _, filenames in os.walk(dest):
        for name in filenames:
            p = os.path.join(dirpath, name)
            if not is_text(p) or name in ("mvnw", "mvnw.cmd", "maven-wrapper.properties"):
                continue
            with open(p, encoding="utf-8-sig") as f:
                for no, line in enumerate(f, 1):
                    if LINT.search(line):
                        problemi.append(f"{os.path.relpath(p, dest)}:{no}: {line.strip()[:100]}")
    if problemi:
        raise GenError("Ranjiva verzija sadrži riječi koje otkrivaju ranjivosti:\n  " + "\n  ".join(problemi))


def generate(stack, mode, dest, s_testovima=False):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    keep_secure = mode == "rjesenje"
    copy_tree(os.path.join(PREDLOZAK, stack), dest, keep_secure)
    if not keep_secure:
        lint(dest)
    if keep_secure or s_testovima:
        copy_tree(os.path.join(PREDLOZAK, f"{stack}-sigurnosni-testovi"), dest, keep_secure)


def paket(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    radni = os.path.join(out_dir, "knjiznica-demo")
    if os.path.exists(radni):
        shutil.rmtree(radni)
    for stack in STACKS:
        generate(stack, "ranjivo", os.path.join(radni, stack))
    shutil.copy2(os.path.join(ROOT, "PROCITAJ-ME.md"), os.path.join(radni, "PROCITAJ-ME.md"))
    zip_path = os.path.join(out_dir, "knjiznica-demo.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, filenames in os.walk(radni):
            for name in sorted(filenames):
                p = os.path.join(dirpath, name)
                arc = os.path.join("knjiznica-demo", os.path.relpath(p, radni))
                info = zipfile.ZipInfo.from_file(p, arc)
                if name in ("mvnw", "run.py"):
                    info.external_attr = 0o100755 << 16
                with open(p, "rb") as f:
                    z.writestr(info, f.read(), zipfile.ZIP_DEFLATED)
    print(zip_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stack", choices=STACKS)
    ap.add_argument("--mode", choices=("ranjivo", "rjesenje"))
    ap.add_argument("--dest")
    ap.add_argument("--s-testovima", action="store_true", help="ranjivoj verziji dodaj i sigurnosne testove")
    ap.add_argument("--paket", metavar="DIR", help="izradi ZIP za polaznike")
    a = ap.parse_args()
    try:
        if a.paket:
            paket(a.paket)
        elif a.stack and a.mode and a.dest:
            generate(a.stack, a.mode, a.dest, a.s_testovima)
            print(a.dest)
        else:
            ap.error("zadaj --paket ili --stack, --mode i --dest")
    except GenError as e:
        print(f"GREŠKA: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
