#!/usr/bin/env python3
"""Završni ispit – Moodle XML za šest kvizova (Java, .NET, Python × probni i pravi ispit).

Pitanja su u četiri modula:
  pitanja_opca.py    – teorijska pitanja neovisna o tehnologiji (zajednička za sve stackove)
  pitanja_java.py    – Java / Spring Boot
  pitanja_dotnet.py  – C# / ASP.NET Core
  pitanja_python.py  – Python / FastAPI

Svaki modul ima popise PROBNI i ISPIT. Generator:
  - provjerava pitanja (lint): 4 odgovora, točno jedan točan, jedinstveni ID-ovi, točan odgovor nije
    prečesto najdulji ni najkraći, nema pojmova iz druge tehnologije, nema „sve/ništa od navedenog”,
  - izrađuje Moodle XML po kategoriji i jedan zajednički XML sa svim kategorijama,
  - izrađuje ključ odgovora za predavača (Markdown).

Pokretanje: python3 generiraj_kviz.py [--izlaz dist]
"""
import argparse
import hashlib
import html
import os
import re
import sys

import pitanja_dotnet
import pitanja_java
import pitanja_opca
import pitanja_python

KORIJEN_KATEGORIJE = "$course$/top/Završni ispit"

# (oznaka, modul, naziv kategorije, zabranjeni pojmovi)
DRUGI_JAVA = [r"\bJava\b", r"\bSpring\b", r"\bMaven\b", r"\bmvnw?\b", r"\bJUnit\b", r"SpotBugs", r"JdbcTemplate",
              r"\bpom\.xml\b", r"SnakeYAML", r"Thymeleaf", r"\bJVM\b", r"\bJDBC\b", r"\bjjwt\b"]
DRUGI_DOTNET = [r"\.NET\b", r"\bC#", r"ASP\.NET", r"NuGet", r"Roslyn", r"\bxUnit\b", r"\bdotnet\b", r"\bcsproj\b",
                r"Newtonsoft", r"YamlDotNet", r"\bRazor\b", r"\bSqlite[A-Z]", r"\bCA\d{4}\b", r"\bNU19"]
DRUGI_PYTHON = [r"\bPython\b", r"FastAPI", r"\bpip\b", r"pip-audit", r"PyPI", r"\bpytest\b", r"\bBandit\b", r"PyYAML",
                r"[Pp]ydantic", r"\buvicorn\b", r"Starlette", r"\bpickle\b", r"[Jj]inja2", r"\bpwdlib\b",
                r"\bhashlib\b", r"\bsqlite3\b", r"\bPyJWT\b", r"\bRuff\b", r"\bdef\b"]

SKUPOVI = [
    ("OPCA", pitanja_opca, "Opća pitanja", DRUGI_JAVA + DRUGI_DOTNET + DRUGI_PYTHON),
    ("JAVA", pitanja_java, "Java", DRUGI_DOTNET + DRUGI_PYTHON),
    ("NET", pitanja_dotnet, ".NET", DRUGI_JAVA + DRUGI_PYTHON),
    ("PY", pitanja_python, "Python", DRUGI_JAVA + DRUGI_DOTNET),
]
VRSTE = [("P", "PROBNI", "probni ispit"), ("I", "ISPIT", "završni ispit")]

NAJVISE_NAJDULJI = 0.30   # udio pitanja u kategoriji u kojima je točan odgovor najdulji
NAJVISE_NAJKRACI = 0.40   # i obrnuto – da pravilo ne postane „uvijek najkraći”
ZABRANJENO_SVUDA = [r"(?i)\bsve od navedenog\b", r"(?i)\bništa od navedenog\b", r"(?i)\bsvi navedeni\b",
                    r"(?i)\boba odgovora\b", r"\]\]>"]

STIL_KODA = ('background:#1b1b22;color:#f2f2f2;padding:8px 10px;border-radius:4px;font-size:90%;'
             'white-space:pre;overflow-x:auto')


class Greska(Exception):
    pass


def kod_html(kod):
    return f'<pre style="{STIL_KODA}"><code>{html.escape(kod)}</code></pre>'


def tekst_html(tekst):
    """Odlomci odvojeni praznim retkom; `x` u tekstu postaje <code>x</code>."""
    dijelovi = []
    for odlomak in tekst.strip().split("\n\n"):
        e = html.escape(odlomak.strip()).replace("\n", "<br>")
        e = re.sub(r"`([^`]+)`", r"<code>\1</code>", e)
        dijelovi.append(f"<p>{e}</p>")
    return "".join(dijelovi)


def inline(tekst):
    e = html.escape(tekst)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", e)


def cist(tekst):
    return tekst.replace("`", "")


def provjeri(skup_oznaka, vrsta, pitanja, zabranjeni, svi_id):
    problemi = []
    najdulji = najkraci = 0
    for p in pitanja:
        pid = p["id"]
        if pid in svi_id:
            problemi.append(f"{pid}: ID se ponavlja")
        svi_id.add(pid)
        odgovori = [p["t"]] + list(p["n"])
        if len(p["n"]) != 3:
            problemi.append(f"{pid}: treba točno 3 netočna odgovora (ima {len(p['n'])})")
        tekstovi = [cist(o[0]).strip() for o in odgovori]
        if len(set(t.lower() for t in tekstovi)) != len(tekstovi):
            problemi.append(f"{pid}: odgovori se ponavljaju")
        for o in odgovori:
            if not o[0].strip() or not o[1].strip():
                problemi.append(f"{pid}: prazan odgovor ili obrazloženje")
        duljine = [len(t) for t in tekstovi]
        if duljine[0] > max(duljine[1:]):
            najdulji += 1
        if duljine[0] < min(duljine[1:]):
            najkraci += 1
        cijeli = " ".join([p["tekst"], p.get("kod") or "", p.get("napomena") or ""] +
                          [o[0] + " " + o[1] for o in odgovori])
        for uzorak in zabranjeni:
            if re.search(uzorak, cijeli):
                problemi.append(f"{pid}: pojam iz druge tehnologije ({uzorak})")
        for uzorak in ZABRANJENO_SVUDA:
            if re.search(uzorak, cijeli):
                problemi.append(f"{pid}: nedopušten izraz ({uzorak})")
    n = len(pitanja)
    if n and najdulji / n > NAJVISE_NAJDULJI:
        problemi.append(f"{skup_oznaka}-{vrsta}: točan odgovor je najdulji u {najdulji}/{n} pitanja "
                        f"(najviše {NAJVISE_NAJDULJI:.0%})")
    if n and najkraci / n > NAJVISE_NAJKRACI:
        problemi.append(f"{skup_oznaka}-{vrsta}: točan odgovor je najkraći u {najkraci}/{n} pitanja")
    return problemi, najdulji, najkraci


def redoslijed(pid):
    """Stalan, ali raznolik položaj točnog odgovora u XML-u (Moodle ionako miješa odgovore)."""
    return int(hashlib.sha256(pid.encode()).hexdigest(), 16) % 4


def pitanje_xml(skup_oznaka, p):
    ime = f"ZI-{skup_oznaka}-{p['id']} {p['naslov']}"
    tekst = tekst_html(p["tekst"]) + (kod_html(p["kod"]) if p.get("kod") else "")
    if p.get("pitanje"):
        tekst += tekst_html(p["pitanje"])
    t_odg, t_zasto = p["t"]
    opce = (f"<p><strong>Točan odgovor:</strong> {inline(t_odg)}</p>"
            f"<p><strong>Zašto je točan:</strong> {inline(t_zasto)}</p>"
            "<p><strong>Zašto ostali odgovori nisu točni:</strong></p><ul>"
            + "".join(f"<li><em>{inline(o)}</em> – {inline(z)}</li>" for o, z in p["n"]) + "</ul>")
    if p.get("napomena"):
        opce += f"<p><strong>Gradivo:</strong> {inline(p['napomena'])}</p>"
    odgovori = [(t_odg, 100, "Točno. " + t_zasto)] + [(o, 0, "Netočno. " + z) for o, z in p["n"]]
    poz = redoslijed(p["id"])
    odgovori = odgovori[1:poz + 1] + [odgovori[0]] + odgovori[poz + 1:]
    out = ['<question type="multichoice">',
           f"<name><text>{html.escape(ime)}</text></name>",
           f'<questiontext format="html"><text><![CDATA[{tekst}]]></text></questiontext>',
           f'<generalfeedback format="html"><text><![CDATA[{opce}]]></text></generalfeedback>',
           "<defaultgrade>1.0000000</defaultgrade>", "<penalty>0.0000000</penalty>", "<hidden>0</hidden>",
           f"<idnumber>ZI-{skup_oznaka}-{p['id']}</idnumber>",
           "<single>true</single>", "<shuffleanswers>true</shuffleanswers>",
           "<answernumbering>abc</answernumbering>", "<showstandardinstruction>0</showstandardinstruction>",
           '<correctfeedback format="html"><text><![CDATA[<p>Točno.</p>]]></text></correctfeedback>',
           '<partiallycorrectfeedback format="html"><text></text></partiallycorrectfeedback>',
           '<incorrectfeedback format="html"><text><![CDATA[<p>Netočno.</p>]]></text></incorrectfeedback>']
    for odg, frakcija, povratna in odgovori:
        out.append(f'<answer fraction="{frakcija}" format="html"><text><![CDATA[{inline(odg)}]]></text>'
                   f'<feedback format="html"><text><![CDATA[<p>{inline(povratna)}</p>]]></text></feedback></answer>')
    out.append("</question>")
    return "\n".join(out)


def kategorija_xml(put):
    return (f'<question type="category"><category><text>{html.escape(put)}</text></category>'
            "<info format=\"html\"><text></text></info></question>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--izlaz", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist"))
    a = ap.parse_args()
    os.makedirs(a.izlaz, exist_ok=True)

    problemi, svi_id, statistika = [], set(), []
    for oznaka, modul, naziv, zabranjeni in SKUPOVI:
        for kratko, atribut, opis in VRSTE:
            pitanja = getattr(modul, atribut)
            ids = {f"{oznaka}-{p['id']}" for p in pitanja}
            pr, nd, nk = provjeri(oznaka, kratko, [dict(p, id=f"{p['id']}") for p in pitanja], zabranjeni, set())
            problemi += pr
            for i in ids:
                if i in svi_id:
                    problemi.append(f"{i}: ID se ponavlja među skupovima")
                svi_id.add(i)
            statistika.append((naziv, opis, len(pitanja), nd, nk))
    if problemi:
        raise Greska("Provjera pitanja nije prošla:\n  " + "\n  ".join(problemi))

    sve = ['<?xml version="1.0" encoding="UTF-8"?>', "<quiz>"]
    kljuc = ["# Završni ispit – ključ odgovora (SAMO ZA PREDAVAČA)", "",
             "| Skup | Vrsta | Pitanja | Točan najdulji | Točan najkraći |", "|---|---|---|---|---|"]
    kljuc += [f"| {s[0]} | {s[1]} | {s[2]} | {s[3]} | {s[4]} |" for s in statistika]
    for oznaka, modul, naziv, _ in SKUPOVI:
        for kratko, atribut, opis in VRSTE:
            put = f"{KORIJEN_KATEGORIJE}/{naziv} – {opis}"
            dio = [kategorija_xml(put)] + [pitanje_xml(oznaka, p) for p in getattr(modul, atribut)]
            ime = f"ZI-{oznaka}-{'probni' if kratko == 'P' else 'ispit'}.xml"
            with open(os.path.join(a.izlaz, ime), "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "\n".join(dio) + "\n</quiz>\n")
            sve += dio
            kljuc += ["", f"## {naziv} – {opis} (`{put}`)", ""]
            for p in getattr(modul, atribut):
                kljuc.append(f"- **ZI-{oznaka}-{p['id']} {p['naslov']}** – {cist(p['t'][0])}")
    sve.append("</quiz>")
    with open(os.path.join(a.izlaz, "ZI-sva-pitanja.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sve) + "\n")
    with open(os.path.join(a.izlaz, "kljuc-odgovora.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(kljuc) + "\n")
    for s in statistika:
        print(f"{s[0]:14} {s[1]:13} {s[2]:3} pitanja · točan najdulji {s[3]:2} · najkraći {s[4]:2}")
    print("XML:", a.izlaz)


if __name__ == "__main__":
    try:
        main()
    except Greska as e:
        print(e, file=sys.stderr)
        sys.exit(1)
