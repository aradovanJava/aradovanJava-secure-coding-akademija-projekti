#!/usr/bin/env python3
"""Detaljno ocjenjivanje predaje (dopuna tools/ocijeni.py, grana ocjenjivanje-t2).

  python3 tools/ocijeni_detalji.py --predaja predaje/V07-Ime-Prezime.zip [--stack java] [--json out.json]

Uz ono što radi ocijeni.py ispisuje:
  A) predaja kakva jest (bez skrivenih testova): rezultati i pokrivenost koda vlastitog skupa testova,
  B) predaja + skriveni testovi: koji skriveni/funkcionalni testovi padaju i s kojom porukom,
  C) testovi polaznika nad izvornom varijantom (crveno → zeleno); testovima polaznika smatra se SVAKA testna
     datoteka koja ne postoji u izvornoj varijanti ili se od nje razlikuje (i u paketu primjer), osim funkcionalnih;
     ako se zajedno ne mogu prevesti, svaka se datoteka pokreće zasebno,
  D) izvorna varijanta s isporučenim testovima – početna pokrivenost (za usporedbu s A),
  E) izmijenjeni funkcionalni testovi (pravilo: ne smiju se mijenjati).
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate as gen            # noqa: E402
import check_results as chk       # noqa: E402
import ocijeni as oc              # noqa: E402

TEST_EXT = {"java": (".java",), "python": (".py",), "dotnet": (".cs",)}


def test_root(stack, proj, domain):
    if stack == "java":
        return os.path.join(proj, "src", "test")
    if stack == "python":
        return os.path.join(proj, "tests")
    return os.path.join(proj, "tests", f"{gen.DOMAINS[domain]}.Tests")


def rel_files(base, exts):
    out = []
    for p in glob.glob(os.path.join(base, "**", "*"), recursive=True):
        if os.path.isfile(p) and p.endswith(exts) and not re.search(r"[/\\](bin|obj|__pycache__)[/\\]", p):
            out.append(os.path.relpath(p, base).replace("\\", "/"))
    return sorted(out)


def junit_details(res_dir):
    """[(classname, name, status, message)] iz JUnit XML i TRX."""
    out = []
    for p in glob.glob(os.path.join(res_dir, "**", "TEST-*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for tc in root.iter("testcase"):
            f = tc.find("failure")
            if f is None:
                f = tc.find("error")
            status = "fail" if f is not None else "skip" if tc.find("skipped") is not None else "pass"
            msg = ""
            if f is not None:
                msg = (f.get("message") or "") + "\n" + "\n".join((f.text or "").splitlines()[:6])
            out.append((tc.get("classname", ""), tc.get("name", ""), status, msg.strip()[:700]))
    ns = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
    for p in glob.glob(os.path.join(res_dir, "**", "*.trx"), recursive=True):
        root = ET.parse(p).getroot()
        defs = {ut.get("id"): ut.find("t:TestMethod", ns) for ut in root.iterfind(".//t:TestDefinitions/t:UnitTest", ns)}
        for r in root.iterfind(".//t:Results/t:UnitTestResult", ns):
            tm = defs.get(r.get("testId"))
            cls = tm.get("className", "").split(",")[0] if tm is not None else ""
            oc_ = r.get("outcome", "")
            status = "pass" if oc_ == "Passed" else "skip" if oc_ in ("NotExecuted", "Inconclusive") else "fail"
            m = r.find(".//t:ErrorInfo/t:Message", ns)
            out.append((cls, tm.get("name", "") if tm is not None else r.get("testName", ""), status,
                        (m.text or "")[:700] if m is not None else ""))
    return out


def owner_of(stack, cls, student_files):
    """Kojoj testnoj datoteci polaznika pripada klasa iz rezultata (ili None)."""
    simple = cls.split(".")[-1].split("$")[0]
    for rel in student_files:
        stem = os.path.splitext(os.path.basename(rel))[0]
        if stack == "python":
            mod = rel[:-3].replace("/", ".")
            if cls.endswith(mod) or cls.split(".")[-1] == stem or f".{stem}." in f".{cls}." or cls.endswith(stem):
                return rel
        elif simple == stem:
            return rel
    return None


def build_tail(res):
    p = os.path.join(res, "build.log")
    if not os.path.exists(p):
        return ""
    txt = open(p, encoding="utf-8", errors="ignore").read()
    errs = [l for l in txt.splitlines() if re.search(r"\[ERROR\]|error CS|ERROR collecting|ImportError|ModuleNotFound", l)]
    return "\n".join(errs[:25]) or txt[-2500:]


def run_single_java(orig_base, rel, src_file, work, i):
    d = os.path.join(work, f"jedan-{i}")
    oc.clean_copy(orig_base, d)
    dst = os.path.join(d, "src", "test", rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src_file, dst)
    res = os.path.join(work, f"rez-jedan-{i}")
    os.makedirs(res, exist_ok=True)
    cls = os.path.splitext(os.path.basename(rel))[0]
    mvnw = os.path.join(d, "mvnw")
    if os.path.exists(mvnw):
        os.chmod(mvnw, 0o755)
    cmd = [mvnw if os.path.exists(mvnw) else "mvn", "-B", "-ntp", "test", f"-Dtest={cls}*",
           "-Dsurefire.failIfNoSpecifiedTests=false", "-Dmaven.test.failure.ignore=true", "-Djacoco.skip=true"]
    oc.run(cmd, d, os.path.join(res, "build.log"))
    sr = os.path.join(d, "target", "surefire-reports")
    if os.path.isdir(sr):
        shutil.copytree(sr, os.path.join(res, "surefire-reports"), dirs_exist_ok=True)
    det = junit_details(res)
    return det, (build_tail(res) if not det else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predaja", required=True)
    ap.add_argument("--variant")
    ap.add_argument("--stack", default="auto")
    ap.add_argument("--json")
    a = ap.parse_args()

    work = tempfile.mkdtemp(prefix="detalji-")
    ex = os.path.join(work, "predaja")
    with zipfile.ZipFile(a.predaja) as z:
        for m in z.namelist():
            t = os.path.realpath(os.path.join(ex, m))
            if not t.startswith(os.path.realpath(ex) + os.sep) and t != os.path.realpath(ex):
                sys.exit(f"Neispravna putanja u ZIP-u: {m}")
        z.extractall(ex)
    variant = a.variant or re.search(r"(V\d\d)", os.path.basename(a.predaja)).group(1)
    v = gen.load_variants()[variant]
    domain, vulnerable = v["domain"], v["vulnerable"]
    projects = oc.find_projects(ex)
    if a.stack != "auto":
        stack = a.stack
    elif len(projects) == 1:
        stack = next(iter(projects))
    else:
        scores = {s: oc.changed_files(s, domain, vulnerable, p, work) for s, p in projects.items()}
        stack = max(scores, key=scores.get)
    proj = projects[stack]
    out = {"predaja": os.path.basename(a.predaja), "variant": variant, "domain": domain, "stack": stack,
           "vulnerable": vulnerable}

    # izvorna varijanta (za usporedbu datoteka i za C/D)
    orig = os.path.join(work, "izvorno-cisto")
    gen.generate(stack, domain, vulnerable, orig, quiet=True, do_lint=False)
    exts = TEST_EXT[stack]
    t_sub, t_orig = test_root(stack, proj, domain), test_root(stack, orig, domain)
    sub_files, orig_files = rel_files(t_sub, exts), set(rel_files(t_orig, exts))
    student, func_changed = [], []
    for rel in sub_files:
        if re.search(r"(^|/)(skriveno|Skriveno)/", rel):
            continue
        same = rel in orig_files and open(os.path.join(t_sub, rel), "rb").read() == open(os.path.join(t_orig, rel), "rb").read()
        if re.search(r"(^|/)(funkcionalno|Funkcionalno)/", rel):
            if not same:
                func_changed.append(rel)
            continue
        if not same and not rel.endswith("__init__.py"):
            student.append(rel)
    func_missing = [r for r in orig_files if re.search(r"(^|/)(funkcionalno|Funkcionalno)/", r) and r not in sub_files]
    out["student_test_files"] = student
    out["functional_changed"] = func_changed
    out["functional_missing"] = func_missing

    # A) predaja kakva jest
    a_dir = os.path.join(work, "A")
    oc.clean_copy(proj, a_dir)
    ok_a, cov_a = oc.run_tests(stack, a_dir, os.path.join(work, "rez-A"))
    det_a = junit_details(os.path.join(work, "rez-A"))
    out["A"] = {"build_ok": ok_a, "coverage": cov_a, "total": len(det_a),
                "failed": [(c.split(".")[-1], n, m[:300]) for c, n, s, m in det_a if s == "fail"],
                "build_errors": "" if det_a else build_tail(os.path.join(work, "rez-A"))}

    # B) predaja + skriveni testovi
    b_dir = os.path.join(work, "B")
    oc.clean_copy(proj, b_dir)
    gen.copy_tree(os.path.join(oc.ROOT, "hidden-tests", stack, domain), gen.hidden_target(stack, domain, b_dir), set(vulnerable))
    ok_b, cov_b = oc.run_tests(stack, b_dir, os.path.join(work, "rez-B"))
    det_b = junit_details(os.path.join(work, "rez-B"))
    slots = {}
    for c, n, s, m in det_b:
        kind, slot = chk.classify(c, n)
        if kind == "skriveno" and slot:
            slots.setdefault(slot, []).append({"test": f"{c.split('.')[-1]}.{n}", "status": s, "msg": m})
    func_fail = [(c.split(".")[-1], n, m) for c, n, s, m in det_b if s == "fail" and chk.classify(c, n)[0] == "funkcionalno"]
    out["B"] = {"build_ok": ok_b, "coverage_with_hidden": cov_b, "slots": slots, "functional_failed": func_fail,
                "functional_total": sum(1 for c, n, s, m in det_b if chk.classify(c, n)[0] == "funkcionalno"),
                "build_errors": "" if det_b else build_tail(os.path.join(work, "rez-B"))}

    # C) testovi polaznika nad izvornim kodom
    sub_status = {}
    for c, n, s, m in det_a:
        f = owner_of(stack, c, student)
        if f:
            sub_status[f"{f}::{n}"] = {"file": f, "cls": c.split(".")[-1], "test": n, "predaja": s, "izvorno": None}
    c_info = {"mode": None, "notes": {}}
    if student:
        c_dir = os.path.join(work, "C")
        oc.clean_copy(orig, c_dir)
        for rel in student:
            dst = os.path.join(test_root(stack, c_dir, domain), rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(t_sub, rel), dst)
        ok_c, _ = oc.run_tests(stack, c_dir, os.path.join(work, "rez-C"))
        det_c = junit_details(os.path.join(work, "rez-C"))
        if det_c:
            c_info["mode"] = "zajedno"
            for c, n, s, m in det_c:
                f = owner_of(stack, c, student)
                if f:
                    k = f"{f}::{n}"
                    sub_status.setdefault(k, {"file": f, "cls": c.split(".")[-1], "test": n, "predaja": None, "izvorno": None})
                    sub_status[k]["izvorno"] = s
        elif stack == "java":
            c_info["mode"] = "pojedinačno"
            c_info["combined_errors"] = build_tail(os.path.join(work, "rez-C"))
            for i, rel in enumerate(student):
                det, err = run_single_java(orig, rel, os.path.join(t_sub, rel), work, i)
                if err:
                    c_info["notes"][rel] = err[:1200]
                for c, n, s, m in det:
                    if owner_of(stack, c, [rel]):
                        k = f"{rel}::{n}"
                        sub_status.setdefault(k, {"file": rel, "cls": c.split(".")[-1], "test": n, "predaja": None, "izvorno": None})
                        sub_status[k]["izvorno"] = s
        else:
            c_info["mode"] = "neuspjelo"
            c_info["combined_errors"] = build_tail(os.path.join(work, "rez-C"))
    out["C"] = {"info": c_info, "tests": list(sub_status.values())}

    # D) izvorna varijanta – početna pokrivenost
    d_dir = os.path.join(work, "D")
    oc.clean_copy(orig, d_dir)
    _, cov_d = oc.run_tests(stack, d_dir, os.path.join(work, "rez-D"))
    out["D"] = {"coverage_baseline": cov_d}

    js = json.dumps(out, ensure_ascii=False, indent=1)
    if a.json:
        open(a.json, "w", encoding="utf-8").write(js)
    import base64, gzip
    b = base64.b64encode(gzip.compress(js.encode("utf-8"))).decode()
    print("===DETALJI-POCETAK===")
    for i in range(0, len(b), 4000):
        print(f"B64 {i // 4000:04d} {b[i:i + 4000]}")
    print("===DETALJI-KRAJ===")
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
