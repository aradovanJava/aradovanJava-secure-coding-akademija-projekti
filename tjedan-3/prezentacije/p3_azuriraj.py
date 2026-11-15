"""P3 – Ispitivanje sigurnosti, rizik i usklađenost (Tjedan 3, Dan 3): sadržaj slajdova na strukturi p3-struct.pptx.

Struktura (29 slajdova) nastala je dupliciranjem slajdova P1 (vidi p3_order.txt). Ova skripta mijenja samo tekst,
tablice i ikone te na slajdu 15 crta dijagram toka podataka. Bilješke govornika: biljeske_p3.py.
"""
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from biljeske_p3 import BILJESKE
from deckkit import (PINK, biljeske, obrisi_oblik, oblik, postavi_kod, postavi_oznaku, postavi_tablicu, postavi_tekst,
                     zamijeni_ikonu)

ULAZ, IZLAZ = sys.argv[1], sys.argv[2]
prs = Presentation(ULAZ)
S = {i + 1: s for i, s in enumerate(prs.slides)}
assert len(S) == 29, len(S)

PREDAVANJE = "TJEDAN 3 · PREDAVANJE 3"
POG = {1: "01 · PIPELINE", 2: "02 · ISPITIVANJE", 3: "03 · MODEL PRIJETNJI", 4: "04 · ANALIZA RIZIKA",
       5: "05 · USKLAĐENOST"}

# SVG dijelovi ikona – dohvatiti PRIJE zamjena (zamjena mijenja r:embed na izvornim slajdovima)
from deckkit import _svg_blip  # noqa: E402

DIJELOVI = {}
for s in prs.slides:
    for sh in s.shapes:
        if sh.shape_type == 13 and sh.name.startswith("Ikona ") and sh.name[6:] not in DIJELOVI:
            DIJELOVI[sh.name[6:]] = s.part.related_part(_svg_blip(sh).get(qn("r:embed")))
RT_IMAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"


def ikona(slide, pic, ime):
    rid = slide.part.relate_to(DIJELOVI[ime], RT_IMAGE)
    _svg_blip(pic).set(qn("r:embed"), rid)
    c = pic._element.find(qn("p:nvPicPr")).find(qn("p:cNvPr"))
    c.set("name", "Ikona " + ime)
    c.set("descr", "Ikona: " + ime)


def naslov(slide, tekst, podnaslov):
    postavi_tekst(oblik(slide, 2), tekst)
    postavi_tekst(oblik(slide, 3), podnaslov)


def poglavlje(slide, tekst, broj, opis):
    postavi_tekst(oblik(slide, 2), tekst)
    postavi_tekst(oblik(slide, 3), str(broj))
    postavi_tekst(oblik(slide, 4), opis)


def dva_runa(shape, odlomci):
    """Odlomci okvira: (oznaka, tekst) za odlomak s dva runa ili str za odlomak s jednim runom; broj odlomaka isti."""
    ps = shape.text_frame._txBody.findall(qn("a:p"))
    assert len(ps) == len(odlomci), (len(ps), len(odlomci))
    for p, o in zip(ps, odlomci):
        runs = p.findall(qn("a:r"))
        if isinstance(o, tuple):
            runs[0].find(qn("a:t")).text = o[0]
            runs[1].find(qn("a:t")).text = o[1]
        else:
            runs[0].find(qn("a:t")).text = o
            for r in runs[1:]:
                p.remove(r)


def retci_okvira(shape, retci):
    """Okvir čiji su odlomci istog stila (jedan run): broj odlomaka prilagođava se (kopija zadnjeg)."""
    import copy
    tx = shape.text_frame._txBody
    ps = tx.findall(qn("a:p"))
    while len(ps) < len(retci):
        novi = copy.deepcopy(ps[-1])
        tx.append(novi)
        ps.append(novi)
    while len(ps) > len(retci):
        tx.remove(ps.pop())
    for p, t in zip(ps, retci):
        runs = p.findall(qn("a:r"))
        runs[0].find(qn("a:t")).text = t
        for r in runs[1:]:
            p.remove(r)


def kartice(slide, kartice_):
    """kartice_ = [(id_kartice, id_naslova, id_opisa, naslov, opis), …]"""
    for kid, nid, oid, n, o in kartice_:
        postavi_tekst(oblik(slide, nid), n)
        postavi_tekst(oblik(slide, oid), o)
        k = oblik(slide, kid)
        k._element.find(qn("p:nvSpPr")).find(qn("p:cNvPr")).set("name", "Kartica " + n[:28])


# ------------------------------------------------------------------ 1: naslov
dva_runa(oblik(S[1], 6), [
    "Ispitivanje sigurnosti, rizik i usklađenost",
    "Radionica na vlastitom projektu",
    "Secure Coding akademija · Tjedan 3 · Predavanje 3",
    "doc. dr. sc. Aleksander Radovan, prof. struč. stud.",
])

# ------------------------------------------------------------------ 2: sadržaj + tjedan
naslov(S[2], "Sadržaj", PREDAVANJE)
for i, (bid, tid, t) in enumerate([
    (4, 5, "Pipeline na vašem repozitoriju"),
    (6, 7, "Ispitivanje razine sigurnosti"),
    (8, 9, "Model prijetnji"),
    (10, 11, "Analiza rizika"),
    (12, 13, "Usklađenost s dokazima"),
], 1):
    postavi_tekst(oblik(S[2], bid), f"{i:02d}")
    postavi_tekst(oblik(S[2], tid), t)
for sid in (14, 15, 16, 17):
    obrisi_oblik(oblik(S[2], sid))
tjedan = oblik(S[2], 20)
dva_runa(tjedan, [
    ("Dan 1  ", "obrane T2; mehanizmi okvira i DevSecOps (P1)"),
    ("Dan 2  ", "sigurnost baza podataka (P2)"),
    ("Dan 3  ", "danas: radionica – ispitivanje, rizik i usklađenost (P3)"),
    ("Dani 4–5  ", "samostalno dovršavanje i predaja u nedjelju"),
    ("Tjedan 4  ", "rad na projektu i završni rad s prezentacijom"),
])
# Dan 3 istaknut bojom
for r in tjedan.text_frame.paragraphs[2].runs:
    r.font.color.rgb = RGBColor.from_string(PINK)

# ------------------------------------------------------------------ 3: ishodi
naslov(S[3], "Ishodi učenja", PREDAVANJE)
kartice(S[3], [
    (4, 152, 153, "Ispitati",
     "razinu sigurnosti vlastite aplikacije: alati i ručni testovi za ono što alati ne vide (OWASP WSTG)"),
    (154, 156, 157, "Automatizirati",
     "sigurnosne provjere u CI/CD pipelineu i dokazati da vrata padaju kad se propust vrati"),
    (158, 160, 161, "Analizirati",
     "prijetnje dijagramom toka podataka i STRIDE-om te rizike kao vjerojatnost × utjecaj"),
    (162, 164, 165, "Dokazati",
     "usklađenost s ASVS-om i propisima (GDPR, NIS2, CRA): zahtjev → kontrola → test → dokaz"),
])
ikona(S[3], oblik(S[3], 151), "monitor_shield")

# ------------------------------------------------------------------ 4: plan radionice
naslov(S[4], "Plan radionice", PREDAVANJE)
for (nid, tid, oid), (t, o) in zip(
        [(5, 5, 6), (8, 8, 9), (11, 11, 12), (14, 14, 15), (17, 17, 18)],
        [("Pipeline", "~45 min · predložak na vašem repozitoriju, zelena vrata i grana u kojoj vrata padaju"),
         ("Ispitivanje", "~40 min · plan prema OWASP WSTG-u, ručni testovi za propuste koje alati ne vide, zapis nalaza"),
         ("Model prijetnji", "~35 min · dijagram toka podataka, granice povjerenja, STRIDE po elementu"),
         ("Analiza rizika", "~25 min · ljestvice, registar rizika, postupanje i preostali rizik"),
         ("Usklađenost", "~40 min · ASVS lista s dokazima, GDPR / NIS2 / CRA za vašu domenu")]):
    postavi_tekst(oblik(S[4], tid), t)
    postavi_tekst(oblik(S[4], oid), o)

# ------------------------------------------------------------------ 5: poglavlje 1
poglavlje(S[5], "Pipeline na vašem repozitoriju", 1,
          "Predložak iz paketa pokrećete na svom T2 projektu – i dokazujete da vrata padaju kad se propust vrati.")

# ------------------------------------------------------------------ 6: šest koraka
naslov(S[6], "Šest koraka do zelenih vrata", POG[1])
kartice(S[6], [
    (4, 43, 44, "Predložak u repozitorij",
     "mapa java/, dotnet/ ili python/ u korijen projekta – sa skrivenim .github i .semgrepignore"),
    (45, 48, 49, "Prvo pokretanje",
     "Actions → Sigurnosna vrata → Summary; prvi put očekujte nalaze, to je polazno stanje"),
    (50, 129, 130, "Ovisnosti",
     "nadogradnja (Dependabot PR); ostatak privremeno u osv-scanner.toml s reason i ignoreUntil"),
    (131, 135, 136, "Tajne i iznimke",
     "prava tajna se opoziva; iznimka je uska: alat, pravilo, datoteka, odsječak, obrazloženje"),
    (137, 140, 141, "DAST s prijavom",
     "svoje putanje u ci/dast-putanje.txt; secret DAST_LOZINKA ako ste promijenili lozinku"),
    (142, 203, 204, "Dokaz pada",
     "u grani vratite jedan T2 propust → vrata NE PROLAZE; spremite poveznicu na pokretanje"),
])

# ------------------------------------------------------------------ 7: kad vrata ne prolaze
naslov(S[7], "Kad vrata ne prolaze", POG[1])
postavi_tablicu(oblik(S[7], 4), [
    ["Simptom", "Vjerojatni uzrok", "Što napraviti"],
    ["OSV: desetci nalaza (Tomcat, Jackson …)", "platforma T2 ima poznate ranjivosti ovisnosti",
     "nadogradnja; ostatak u osv-scanner.toml s rokom"],
    ["nalaz i na popravljenom kodu", "alat ne razlikuje popravak (npr. ORDER BY s popisa)",
     "pojednostavite kod; tek onda uska iznimka"],
    ["gitleaks blokira staru povijest", "tajna je nekad bila u repozitoriju",
     "prava tajna: opozovite je; lažna: .gitleaksignore"],
    ["DAST: aplikacija se ne pokreće", "promijenjena lozinka, port ili konfiguracija",
     "log u artefaktu izvjestaj-dast; DAST_LOZINKA"],
    ["„izvještaj nedostaje” – vrata padaju", "posao je pao ili alat nije radio (fail-closed)",
     "popravite posao – „nije radio” ≠ „ništa nije našao”"],
], sirine=[3.0, 3.1, 3.1], podebljaj_prvi_stupac=False)
dva_runa(oblik(S[7], 5), [("Pravilo: ", "iznimka mora biti uža od nalaza – s odsječkom koda koji postoji samo u "
                                        "ispravnoj verziji, inače sakrije i vraćeni propust.")])

# ------------------------------------------------------------------ 8: poglavlje 2
poglavlje(S[8], "Ispitivanje razine sigurnosti", 2,
          "Alati pokrivaju poznate obrasce. Logiku – tuđi zapis, utrku, fail-open – ispitujete vi.")

# ------------------------------------------------------------------ 9: ispitivanje kao postupak
naslov(S[9], "Ispitivanje kao postupak", POG[2])
for (tid, oid), (t, o) in zip([(5, 6), (9, 10), (13, 14), (17, 18)], [
    ("Opseg", ["što ispitujete i što ne", "okolina, uloge, podaci"]),
    ("Plan", ["OWASP WSTG v4.2", "ASVS razina L1 + odabrani L2"]),
    ("Izvođenje", ["alati iz pipelinea", "+ ručni testovi s dva korisnika"]),
    ("Izvještaj", ["nalaz, dokaz, ozbiljnost", "popravak i ponovno ispitivanje"]),
]):
    postavi_tekst(oblik(S[9], tid), t)
    retci_okvira(oblik(S[9], oid), o)
dva_runa(oblik(S[9], 19), [
    "Za vaš projekt",
    "plan na jednoj stranici: opseg, alati, ručni testovi i kriterij prolaza (vrata zelena, svi sigurnosni testovi prolaze)",
    "ispitujete samo lokalnu ili svoju testnu instancu – tuđi sustav nikad bez pisanog dopuštenja vlasnika",
])

# ------------------------------------------------------------------ 10: što alati ne vide
naslov(S[10], "Što alati iz pipelinea ne vide", POG[2])
postavi_tablicu(oblik(S[10], 4), [
    ["T2 propust", "Zašto ga alat ne vidi", "Kako ga ispitati (WSTG v4.2 · ASVS 5.0)"],
    ["S01 IDOR (brisanje)", "alat ne zna čiji je zapis",
     "ana briše markov zapis → 403/404 · ATHZ-04 · 8.2.2"],
    ["S09 pohranjeni XSS", "pasivni ZAP ne sprema unos pa ne otvara ispis",
     "<script> u tekstu → na ispisu kodirano · INPV-02 · 1.2.1"],
    ["S10 utrka", "pojedinačni zahtjev uvijek prolazi ispravno",
     "10 istodobnih zahtjeva → točno 1 uspjeh · BUSL-05 · 2.3.4"],
    ["S12 logiranje", "alat ne čita log i ne zna što je osjetljivo",
     "uhvatite log u testu: bez lozinke i OIB-a · 16.2.5, 16.3.1"],
    ["S13 fail-open", "iznimka nastaje samo na rubnom ulazu",
     "format=xml na tuđem dokumentu → 4xx · ERRH-01 · 16.5.3"],
], sirine=[1.9, 3.0, 4.3], podebljaj_prvi_stupac=True)
dva_runa(oblik(S[10], 5), [("Poruka: ", "za ove propuste jedina automatska zaštita od regresije je sigurnosni "
                                        "test u build poslu – zato ostaju u pipelineu.")])

# ------------------------------------------------------------------ 11: ručni test i test istodobnosti
naslov(S[11], "Ručni test i test istodobnosti", POG[2])
postavi_oznaku(oblik(S[11], 5), "HTTP", "dva korisnika, jedan zapis")
postavi_kod(oblik(S[11], 6), [
    "@host = http://localhost:8080",
    ("# tokene dobijete s POST /api/auth/login", "c"),
    "@ana = ZALIJEPI_TOKEN_ANE",
    "@marko = ZALIJEPI_TOKEN_MARKA",
    "",
    ("### S01: ana briše markovu rezervaciju", "c"),
    ("DELETE {{host}}/api/rezervacije/2", "h"),
    "Authorization: Bearer {{ana}}",
    ("# očekivano 403 ili 404 – nikako 204", "c"),
    "",
    ("### marko i dalje vidi svoj zapis", "c"),
    "GET {{host}}/api/rezervacije/moje",
    "Authorization: Bearer {{marko}}",
    "",
    ("### S13: nepoznat format, tuđi nalaz", "c"),
    ("GET {{host}}/api/nalazi/1?format=xml", "h"),
    "Authorization: Bearer {{marko}}",
    ("# 4xx, bez sadržaja i teksta iznimke", "c"),
])
postavi_oznaku(oblik(S[11], 8), "Python", "pytest – S10, zadnje mjesto")
postavi_kod(oblik(S[11], 9), [
    ("# posluzitelj: stvarni uvicorn; tokeni: 10 korisnika", "c"),
    "def test_zadnje_mjesto(posluzitelj, tokeni):",
    "    start = threading.Barrier(len(tokeni))",
    "",
    "    def rezerviraj(token: str) -> int:",
    ("        start.wait()          # svi kreću zajedno", "h"),
    "        r = httpx.post(",
    '            f"{posluzitelj}/api/rezervacije",',
    '            headers={"Authorization": f"Bearer {token}"},',
    '            json={"terminId": 7, "napomena": "test",',
    '                  "oib": "48291736504"})',
    "        return r.status_code",
    "",
    "    with ThreadPoolExecutor(len(tokeni)) as ex:",
    "        kodovi = list(ex.map(rezerviraj, tokeni))",
    ("    assert kodovi.count(201) == 1   # kapacitet 1", "h"),
    "    assert kodovi.count(409) == len(tokeni) - 1",
])

# ------------------------------------------------------------------ 12: CVSS 4.0
naslov(S[12], "Ozbiljnost nalaza: CVSS 4.0", POG[2])
postavi_tablicu(oblik(S[12], 4), [
    ["Metrika", "IDOR (VulnShop Lab01)", "Obrazloženje"],
    ["AV – vektor napada", "N (mreža)", "napad preko HTTP API-ja"],
    ["AC / AT – složenost / preduvjeti", "L / N", "nema posebnih uvjeta ni pripreme"],
    ["PR – potrebne ovlasti", "L (niske)", "dovoljan je običan prijavljeni korisnik"],
    ["UI – interakcija korisnika", "N (nije potrebna)", "žrtva ne mora ništa napraviti"],
    ["VC / VI / VA – ranjivi sustav", "H / N / N", "čitanje tuđih podataka, bez izmjene i prekida"],
    ["SC / SI / SA – drugi sustavi", "N / N / N", "nema utjecaja izvan aplikacije"],
], sirine=[2.7, 2.5, 4.0], podebljaj_prvi_stupac=True)
for red in oblik(S[12], 4).table.rows:
    red.height = Emu(300000)
oblik(S[12], 5).top = Inches(3.95)
dva_runa(oblik(S[12], 5), [
    ("Vektor: ", "CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N → 7,1 (visoka)."),
    "CVSS mjeri ozbiljnost, ne rizik. Za ovisnosti dodajte EPSS (vjerojatnost iskorištavanja u 30 dana) i "
    "CISA KEV (dokazano iskorištene), npr. CVE-2025-30066 (tj-actions) je u KEV-u.",
])

# ------------------------------------------------------------------ 13: zapis nalaza
naslov(S[13], "Zapis nalaza", POG[2])
kartice(S[13], [
    (4, 234, 235, "Što i gdje",
     "naslov, endpoint ili datoteka:redak, CWE, ASVS zahtjev i CVSS vektor"),
    (236, 238, 239, "Dokaz",
     "zahtjev i odgovor bez tajni i stvarnih osobnih podataka; koraci za ponavljanje"),
    (240, 242, 243, "Uzrok i popravak",
     "uzrok u kodu, commit s popravkom i sigurnosni test koji je bio crven, a sada je zelen"),
    (244, 272, 273, "Ponovno ispitivanje",
     "isti koraci nakon popravka; status: otvoren · popravljen · prihvaćen rizik"),
])
ikona(S[13], oblik(S[13], 237), "certificate")
ikona(S[13], oblik(S[13], 241), "gears")
ikona(S[13], oblik(S[13], 271), "refresh")

# ------------------------------------------------------------------ 14: poglavlje 3
poglavlje(S[14], "Model prijetnji", 3,
          "Što gradimo? Što može poći po zlu? Što ćemo poduzeti? Jesmo li to dobro napravili?")

# ------------------------------------------------------------------ 15: DFD (crtež)
naslov(S[15], "Dijagram toka podataka (DFD)", POG[3])
for sh in list(S[15].shapes):
    if sh.shape_id not in (2, 3):
        obrisi_oblik(sh)

CRNA, SIVA_T, SIVA_P = "000000", "5A5A5A", "F4F4F4"
sl15 = S[15]


def _tekst(shape, retci, sz=9, boja=CRNA, prvi_bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(36000)
    tf.margin_top = tf.margin_bottom = Emu(18000)
    tf.vertical_anchor = anchor
    for i, t in enumerate(retci):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = t
        f = r.font
        f.size = Pt(sz if i == 0 else sz - 1)
        f.bold = bool(prvi_bold and i == 0)
        f.name = "Work Sans"
        f.color.rgb = RGBColor.from_string(boja if i == 0 else SIVA_T)


def _bez_sjene(shape):
    sp = shape._element.spPr
    if sp.find(qn("a:effectLst")) is None:
        etree.SubElement(sp, qn("a:effectLst"))
    st = shape._element.find(qn("p:style"))
    if st is not None:
        shape._element.remove(st)


def entitet(x, y, w, h, retci):
    s = sl15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    _bez_sjene(s)
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string(SIVA_P)
    s.line.fill.background()
    _tekst(s, retci)
    s.name = "DFD entitet " + retci[0]
    return s


def proces(x, y, w, h, retci):
    s = sl15.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    _bez_sjene(s)
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string("FFFFFF")
    s.line.color.rgb = RGBColor.from_string(PINK)
    s.line.width = Pt(1.5)
    _tekst(s, retci)
    s.name = "DFD proces " + retci[0]
    return s


def crta(x1, y1, x2, y2, boja=SIVA_T, sirina=1.0, strelica=False, isprekidano=False):
    c = sl15.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    st = c._element.find(qn("p:style"))
    if st is not None:
        c._element.remove(st)
    c.line.color.rgb = RGBColor.from_string(boja)
    c.line.width = Pt(sirina)
    if isprekidano:
        c.line.dash_style = MSO_LINE.DASH
    if strelica:
        ln = c.line._get_or_add_ln()
        etree.SubElement(ln, qn("a:tailEnd"), type="triangle", w="med", len="med")
    return c


def spremiste(x, y, w, h, tekst):
    s = sl15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    _bez_sjene(s)
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string("FFFFFF")
    s.line.fill.background()
    _tekst(s, [tekst], sz=9)
    s.name = "DFD spremište " + tekst
    crta(x, y, x + w, y, boja=CRNA, sirina=1.25)
    crta(x, y + h, x + w, y + h, boja=CRNA, sirina=1.25)
    return s


def tok(x1, y1, x2, y2, oznaka=None, ox=None, oy=None, ow=0.75, obostrano=False):
    c = crta(x1, y1, x2, y2, boja=PINK, sirina=1.25, strelica=True)
    if obostrano:
        ln = c.line._get_or_add_ln()
        rep = ln.find(qn("a:tailEnd"))
        rep.addprevious(etree.Element(qn("a:headEnd"), type="triangle", w="med", len="med"))
    if oznaka:
        t = sl15.shapes.add_textbox(Inches(ox), Inches(oy), Inches(ow), Inches(0.3))
        _tekst(t, oznaka.split("\n"), sz=8, boja=SIVA_T, prvi_bold=False)
        for p in t.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(7.5)
                r.font.color.rgb = RGBColor.from_string(SIVA_T)
        t.name = "DFD oznaka " + oznaka.replace("\n", " ")


def granica(x, y, w, h, oznaka):
    s = sl15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    _bez_sjene(s)
    s.fill.background()
    s.line.color.rgb = RGBColor.from_string(PINK)
    s.line.width = Pt(1.0)
    s.line.dash_style = MSO_LINE.DASH
    s.name = "DFD granica " + oznaka
    t = sl15.shapes.add_textbox(Inches(x + 0.08), Inches(y + 0.04), Inches(w - 0.16), Inches(0.2))
    _tekst(t, [oznaka], sz=7.5, boja=PINK, prvi_bold=True, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP)
    t.name = "DFD oznaka granice"


# zone (granice povjerenja) – prve, da budu ispod ostalog
granica(2.45, 1.30, 4.95, 1.98, "GRANICA POVJERENJA · POSLUŽITELJ APLIKACIJE")
granica(2.45, 3.50, 4.95, 1.28, "GRANICA POVJERENJA · CI/CD (GITHUB)")

# aplikacija
entitet(0.42, 1.75, 1.25, 0.55, ["Korisnik", "preglednik / klijent"])
entitet(0.42, 2.62, 1.25, 0.55, ["E-pošta", "reset lozinke"])
proces(2.95, 1.70, 1.55, 1.00, ["API", "Spring · ASP.NET · FastAPI"])
spremiste(5.25, 1.62, 1.95, 0.36, "Baza (SQL Server)")
spremiste(5.25, 2.15, 1.95, 0.36, "Dokumenti (nalazi, računi …)")
spremiste(5.25, 2.68, 1.95, 0.36, "Log")
tok(1.67, 2.02, 2.95, 2.12, "HTTPS + token", 1.70, 1.74, 0.74, obostrano=True)
tok(3.10, 2.52, 1.67, 2.90, "poveznica\nza reset", 1.72, 2.96, 0.70)
tok(4.50, 2.05, 5.25, 1.82, "SQL · TLS", 4.52, 1.62, 0.72, obostrano=True)
tok(4.50, 2.25, 5.25, 2.33, obostrano=True)
tok(4.36, 2.50, 5.25, 2.86, "događaji", 4.48, 2.78, 0.72)

# CI/CD
entitet(0.42, 3.86, 1.25, 0.55, ["Programer"])
spremiste(2.75, 3.98, 1.60, 0.36, "Repozitorij + tajne")
proces(4.70, 3.80, 1.55, 0.76, ["GitHub Actions", "pipeline"])
entitet(7.60, 3.86, 1.95, 0.55, ["Registar paketa", "Maven · NuGet · PyPI"])
tok(1.67, 4.14, 2.75, 4.16, "push / PR", 1.72, 3.86, 0.72)
tok(4.35, 4.16, 4.70, 4.18)
tok(7.60, 4.14, 6.25, 4.18, "ovisnosti", 6.55, 3.86, 0.72)
tok(5.30, 3.80, 3.95, 2.66, "artefakt (isporuka)", 4.98, 3.29, 1.30)

# legenda
lx, ly = 7.60, 1.38
lg = sl15.shapes.add_textbox(Inches(lx), Inches(ly), Inches(1.9), Inches(0.22))
_tekst(lg, ["Legenda"], sz=9, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP)
lg.text_frame.paragraphs[0].runs[0].font.name = "Inria Serif"
lg.name = "DFD legenda"
stavke = [("vanjski entitet", "e"), ("proces", "p"), ("spremište podataka", "s"), ("tok podataka", "t"),
          ("granica povjerenja", "g")]
for i, (t, v) in enumerate(stavke):
    y = ly + 0.34 + i * 0.30
    if v == "e":
        s = sl15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(lx), Inches(y), Inches(0.34), Inches(0.18))
        _bez_sjene(s)
        s.fill.solid(); s.fill.fore_color.rgb = RGBColor.from_string(SIVA_P); s.line.fill.background()
    elif v == "p":
        s = sl15.shapes.add_shape(MSO_SHAPE.OVAL, Inches(lx), Inches(y - 0.02), Inches(0.34), Inches(0.22))
        _bez_sjene(s)
        s.fill.solid(); s.fill.fore_color.rgb = RGBColor.from_string("FFFFFF")
        s.line.color.rgb = RGBColor.from_string(PINK); s.line.width = Pt(1.25)
    elif v == "s":
        crta(lx, y, lx + 0.34, y, boja=CRNA, sirina=1.25)
        crta(lx, y + 0.18, lx + 0.34, y + 0.18, boja=CRNA, sirina=1.25)
    elif v == "t":
        crta(lx, y + 0.09, lx + 0.34, y + 0.09, boja=PINK, sirina=1.25, strelica=True)
    else:
        crta(lx, y + 0.09, lx + 0.34, y + 0.09, boja=PINK, sirina=1.0, isprekidano=True)
    tb = sl15.shapes.add_textbox(Inches(lx + 0.45), Inches(y - 0.04), Inches(1.45), Inches(0.24))
    _tekst(tb, [t], sz=8.5, prvi_bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    tb.name = "DFD legenda " + t

# ------------------------------------------------------------------ 16: STRIDE po elementu
naslov(S[16], "STRIDE po elementu", POG[3])
postavi_tablicu(oblik(S[16], 4), [
    ["Element DFD-a", "Prijetnje", "Primjer u T2 projektu"],
    ["Vanjski entitet (korisnik)", "S, R", "ukradeni token; „nisam ja otkazao termin” bez zapisa (S12)"],
    ["Proces (API)", "S, T, R, I, D, E", "fail-open (S13) → E; utrka (S10) → T; stack trace → I"],
    ["Spremište (baza, datoteke, log)", "T, I, D (+ R za log)", "path traversal (S02) → I; SQLi u sortiranju (S08) → T, I"],
    ["Tok podataka", "T, I, D", "HTTP bez TLS-a; CORS reflektira Origin (S04) → I"],
    ["Prijelaz granice povjerenja", "mjesto kontrole", "autentikacija, autorizacija, validacija – svaki put"],
], sirine=[2.6, 1.8, 4.8], podebljaj_prvi_stupac=True)
dva_runa(oblik(S[16], 5), [("Pravilo: ", "za svaku prijetnju upišite postojeću kontrolu ili je prenesite u "
                                         "registar rizika – prijetnja bez odgovora je nalaz.")])

# ------------------------------------------------------------------ 17: baza i CI/CD
naslov(S[17], "Prijetnje izvan koda aplikacije", POG[3])
postavi_tablicu(oblik(S[17], 4), [
    ["STRIDE", "Baza (P2)", "CI/CD (P1)"],
    ["S – lažno predstavljanje", "jedan zajednički račun za sve aplikacije", "ukradeni token ili PAT s preširokim ovlastima"],
    ["T – neovlaštena izmjena", "izmjena mimo aplikacije (db_owner za aplikaciju)",
     "akcija po pomičnoj oznaci (tj-actions, 2025) → SHA"],
    ["R – poricanje", "nema revizije: tko je čitao OIB?", "nema zaštite grane, force-push na main"],
    ["I – otkrivanje podataka", "nešifrirane kopije, OIB u čistom tekstu", "tajne u logu; pull_request_target s kodom iz PR-a"],
    ["D – uskraćivanje usluge", "upit bez ograničenja zaključa tablicu", "pipeline bez vremenskog ograničenja"],
    ["E – podizanje ovlasti", "TRUSTWORTHY + vlasnik sa → db_owner postaje sysadmin",
     "permissions: write-all; self-hosted runner za tuđe PR-ove"],
], sirine=[2.1, 3.4, 3.7], podebljaj_prvi_stupac=True)
for red in oblik(S[17], 4).table.rows:
    red.height = Emu(340000)

# ------------------------------------------------------------------ 18: poglavlje 4
poglavlje(S[18], "Analiza rizika", 4,
          "Od prijetnje do odluke: koliko je vjerojatno, koliko boli i tko prihvaća ono što ostane.")

# ------------------------------------------------------------------ 19: od prijetnje do preostalog rizika
naslov(S[19], "Od prijetnje do preostalog rizika", POG[4])
for (tid, oid), (t, o) in zip([(5, 6), (9, 10), (13, 14), (17, 18), (21, 22), (25, 26)], [
    ("Prijetnja", ["STRIDE na DFD-u"]),
    ("Ranjivost", ["nalaz ili slabost", "(CWE)"]),
    ("Posljedica", ["podaci, novac,", "ugled, propisi"]),
    ("V × U", ["ljestvice 1–3", "rizik 1–9"]),
    ("Postupanje", ["izbjeći · smanjiti", "prenijeti · prihvatiti"]),
    ("Preostali", ["rizik nakon mjere", "+ odluka vlasnika"]),
]):
    postavi_tekst(oblik(S[19], tid), t)
    retci_okvira(oblik(S[19], oid), o)
from deckkit import postavi_odlomke  # noqa: E402

postavi_odlomke(oblik(S[19], 27), ["Vjerojatnost",
                                   "koliko je lako: treba li prijava, alat, posebno znanje?",
                                   "postoji li javni exploit (EPSS, KEV)?"])
postavi_odlomke(oblik(S[19], 28), ["Utjecaj",
                                   "koji podaci: zdravstveni, OIB, plaće?",
                                   "koliko korisnika i koje obveze (GDPR, NIS2)?"])
postavi_odlomke(oblik(S[19], 290), ["Vlasnik rizika",
                                    "prihvaćanje rizika odobrava poslovni vlasnik, ne programer",
                                    "prihvaćeni rizik ima rok ponovne procjene"])

# ------------------------------------------------------------------ 20: ljestvice
naslov(S[20], "Ljestvice vjerojatnosti i utjecaja", POG[4])
postavi_tablicu(oblik(S[20], 4), [
    ["Razina", "Vjerojatnost (V)", "Utjecaj (U)"],
    ["1 – niska", "treba unutarnji pristup, povlašteni račun ili rijetke uvjete",
     "zanemarivi podaci, bez obveze prijave"],
    ["2 – srednja", "treba posebno znanje, pripremu ili prethodni korak (npr. curenje baze)",
     "osobni podaci manjeg broja korisnika, kraći prekid rada"],
    ["3 – visoka", "dovoljan je običan korisnik (otvorena registracija), alat ili javni exploit",
     "zdravstveni podaci, OIB, plaće; obveza prijave povrede ili incidenta"],
], sirine=[1.4, 3.9, 3.9], podebljaj_prvi_stupac=True)
dva_runa(oblik(S[20], 5), [
    ("Rizik = V × U: ", "1–2 nizak (prihvatiti uz praćenje) · 3–4 srednji (smanjiti u dogovorenom roku) · "
                        "6–9 visok (smanjiti prije isporuke)."),
    "Ljestvice su dogovor tima: zapišite ih uz registar i primjenjujte jednako. Detaljniji modeli: OWASP Risk "
    "Rating Methodology, ISO/IEC 27005.",
])

# ------------------------------------------------------------------ 21: riješeni registar (VulnShop)
naslov(S[21], "Riješeni primjer: registar rizika za VulnShop", POG[4])
postavi_tablicu(oblik(S[21], 4), [
    ["Rizik", "V", "U", "R", "Postupanje", "Mjera i dokaz", "R nakon"],
    ["Lab01: čitanje tuđih narudžbi (IDOR)", "3", "3", "9", "smanjiti",
     "vlasnik u upitu; test „tuđa narudžba → 404”", "3"],
    ["Lab05: ranjiva ovisnost (Text4Shell / jinja2)", "3", "3", "9", "smanjiti",
     "nadogradnja; SCA u vratima; SBOM", "3"],
    ["Lab12: krivotvoreni JWT (alg: none)", "3", "3", "9", "smanjiti",
     "allowlista algoritma, jaka tajna, exp; 3 testa", "3"],
    ["Lab06: MD5 lozinke nakon curenja baze", "2", "3", "6", "smanjiti",
     "Argon2id / bcrypt; test različitih hasheva", "3"],
    ["Lab15: fail-open kod iznimke", "2", "3", "6", "smanjiti",
     "iznimka → odbijanje; test s neispravnim ulazom", "3"],
    ["Kratka nedostupnost pretrage (DoS)", "2", "1", "2", "prihvatiti",
     "rate limit, praćenje; odluka vlasnika s rokom", "2"],
], sirine=[2.65, 0.3, 0.3, 0.33, 0.9, 3.1, 0.72], podebljaj_prvi_stupac=False)
for red in oblik(S[21], 4).table.rows:
    red.height = Emu(300000)
oblik(S[21], 5).top = Inches(3.95)
dva_runa(oblik(S[21], 5), [
    ("Kako čitati: ", "„R nakon” je rizik uz uvedenu mjeru. Ostane li 6 ili više, mjera nije dovoljna – ili "
                      "vlasnik rizika pisano prihvaća rizik s rokom."),
    "V = vjerojatnost, U = utjecaj (1–3), R = V × U. Primjer je namjerno na VulnShopu iz 1. tjedna – svoj registar "
    "radite za svoju domenu.",
])

# ------------------------------------------------------------------ 22: poglavlje 5
poglavlje(S[22], "Usklađenost s dokazima", 5,
          "Usklađenost nije tvrdnja nego trag: zahtjev → kontrola → test → dokaz.")

# ------------------------------------------------------------------ 23: valjan dokaz
naslov(S[23], "Što je valjan dokaz", POG[5])
kartice(S[23], [
    (4, 188, 189, "Test",
     "sigurnosni test koji je bio crven na ranjivom kodu i zelen nakon popravka – naziv testa i commit"),
    (190, 236, 237, "Izvještaj alata",
     "Summary sigurnosnih vrata, SARIF, SBOM ili ZAP izvještaj – s datumom i commitom"),
    (238, 240, 241, "Konfiguracija i kod",
     "isječak ili commit: deny by default, popis origina, zaglavlja, pravilo u ci/semgrep"),
    (242, 244, 245, "Stanje baze",
     "izlaz provjere iz SQL Server laboratorija: ovlasti, RLS, šifriranje (P2)"),
])
ikona(S[23], oblik(S[23], 187), "checklist")
ikona(S[23], oblik(S[23], 239), "door")

# ------------------------------------------------------------------ 24: ASVS s dokazima
naslov(S[24], "ASVS lista s dokazima (primjer)", POG[5])
postavi_tablicu(oblik(S[24], 4), [
    ["ASVS 5.0", "Zahtjev (skraćeno)", "Prije (T2)", "Poslije", "Dokaz"],
    ["8.2.2 (L1)", "pristup zapisu samo ovlaštenom", "S01: briše tuđi zapis", "vlasnik u upitu",
     "test S01 + commit"],
    ["3.4.2 (L1)", "CORS samo s popisa origina", "S04: reflektira Origin", "popis iz konfiguracije",
     "ZAP kuka, Semgrep pravilo"],
    ["2.3.4 (L2)", "ograničeni resurs bez dvostruke rezervacije", "S10: provjeri pa upiši",
     "atomski uvjetni UPDATE", "test s 10 istodobnih zahtjeva"],
    ["16.2.5 (L2)", "osjetljivi podaci ne idu u log", "S12: lozinka i OIB u logu", "maskiranje OIB-a",
     "test s hvatanjem loga"],
    ["15.2.1 (L1)", "komponente u rokovima za zakrpe", "S06: ranjiva YAML bibl.", "nadogradnja",
     "SBOM + OSV, Summary vrata"],
], sirine=[1.05, 2.45, 1.95, 1.75, 2.0], podebljaj_prvi_stupac=True)

# ------------------------------------------------------------------ 25: propisi za domenu
naslov(S[25], "Propisi za vašu domenu", POG[5])
postavi_tablicu(oblik(S[25], 4), [
    ["Domena", "GDPR", "NIS2 / Zakon o kibernetičkoj sigurnosti", "Prvo pitanje za naručitelja"],
    ["MedTermin – poliklinika", "zdravstveni podaci (čl. 9); vjerojatno procjena učinka (čl. 35)",
     "zdravstvo je sektor visoke kritičnosti – u opsegu ovisno o veličini i kategorizaciji",
     "tko je voditelj, a tko izvršitelj obrade (čl. 28)?"],
    ["Ulaznica – prodaja ulaznica", "kupci i OIB; kartice obrađuje pružatelj plaćanja",
     "uglavnom izvan opsega, osim ako je online tržnica ili dio subjekta u opsegu",
     "koliko dugo čuvamo narudžbe i OIB?"],
    ["Kadrovska – HR portal", "podaci zaposlenika i plaće; pravila za radni odnos (čl. 88)",
     "ovisi o djelatnosti tvrtke – portal je dio njezina sustava",
     "tko smije vidjeti platne liste i kako se to bilježi?"],
], sirine=[1.75, 2.6, 2.75, 2.1], podebljaj_prvi_stupac=True)
for i, red in enumerate(oblik(S[25], 4).table.rows):
    red.height = Emu(420000 if i == 0 else 640000)
nap = S[25].shapes.add_textbox(Inches(0.42), Inches(4.05), Inches(9.1), Inches(0.5))
nap.name = "Napomena propisi"
tf = nap.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
p = tf.paragraphs[0]
for tekst, bold, boja in [("Napomena: ", True, PINK),
                          ("ovo nije pravna procjena – opseg NIS2 ovisi o veličini, djelatnosti i kategorizaciji "
                           "subjekta. Obveza prijave povrede osobnih podataka (GDPR čl. 33) vrijedi u sve tri domene.",
                           False, "000000")]:
    r = p.add_run()
    r.text = tekst
    r.font.size = Pt(10)
    r.font.bold = bold
    r.font.name = "Work Sans"
    r.font.color.rgb = RGBColor.from_string(boja)

# ------------------------------------------------------------------ 26: pitanja vodilje
naslov(S[26], "Pitanja vodilje za analizu usklađenosti", POG[5])
kartice(S[26], [
    (4, 234, 235, "Koje podatke obrađujemo?",
     "popis osobnih podataka po tablici, datoteci i logu; posebne kategorije; rok čuvanja"),
    (236, 238, 239, "Tko je odgovoran?",
     "voditelj i izvršitelj obrade, vlasnik rizika, kontakt za incidente i ranjivosti"),
    (240, 242, 243, "Kako dokazujemo kontrole?",
     "ASVS lista: svi L1 zahtjevi koji se odnose na aplikaciju + odabrani L2, svaki s dokazom"),
    (244, 272, 273, "Što kad pođe po zlu?",
     "GDPR: AZOP u 72 h · NIS2: 24 h / 72 h / 1 mj. · CRA (od 11. 9. 2026.): 24 h / 72 h / 14 dana"),
])
ikona(S[26], oblik(S[26], 237), "certificate")
ikona(S[26], oblik(S[26], 241), "gears")
ikona(S[26], oblik(S[26], 271), "refresh")

# ------------------------------------------------------------------ 27: AI asistenti
naslov(S[27], "AI asistenti u radionici", "RADIONICA · PRAVILA RADA")
kartice(S[27], [
    (4, 188, 189, "Bez tajni i osobnih podataka",
     "u upit ne idu ključevi, lozinke, OIB ni stvarni podaci – samo seed podaci iz projekta"),
    (190, 236, 237, "Provjerite generirani kod",
     "AI prijedlog je nepouzdan ulaz: prolazi isti pipeline, testove i pregled kao vaš kod"),
    (238, 240, 241, "Izmišljeni paketi",
     "AI zna predložiti paket koji ne postoji ili je zlonamjeran – provjerite registar i SBOM"),
    (242, 244, 245, "Navedite i provjerite izvore",
     "u izvještaju označite što je nastalo uz AI; provjerite svaki ASVS ID, CVE i članak propisa"),
])
ikona(S[27], oblik(S[27], 187), "file_lock")
ikona(S[27], oblik(S[27], 239), "package")
ikona(S[27], oblik(S[27], 243), "doc_check")

# ------------------------------------------------------------------ 28: zadaci
naslov(S[28], "Zadaci za samostalni rad (dani 4–5)", "TJEDAN 3")
for (tid, oid), (t, o) in zip([(5, 6), (8, 9), (11, 12), (14, 15), (17, 18)], [
    ("DevSecOps pipeline", "vrata zelena na main + grana u kojoj vrata padaju na vraćenom propustu"),
    ("Mehanizmi okvira", "barem dva mjesta s ručnom provjerom prebaci na Spring Security / ASP.NET Core / FastAPI"),
    ("Sigurnost baze", "SQL Server lab za svoju domenu (P2) – skripta i izlaz provjere"),
    ("Prijetnje i rizik", "DFD s granicama povjerenja, STRIDE tablica i registar od barem 5 rizika"),
    ("Usklađenost i kviz", "ASVS lista s dokazima, kratka GDPR/NIS2 analiza; kviz Tjedna 3"),
]):
    postavi_tekst(oblik(S[28], tid), t)
    postavi_tekst(oblik(S[28], oid), o)

# ------------------------------------------------------------------ 29: kraj
dva_runa(oblik(S[29], 6), ["Pitanja?", "Sljedeće: Tjedan 4 – rad na projektu i završni rad"])

# ------------------------------------------------------------------ bilješke
assert sorted(BILJESKE) == list(range(1, 30)), sorted(BILJESKE)
for i, s in S.items():
    biljeske(s, BILJESKE[i])

prs.save(IZLAZ)
print("spremljeno:", IZLAZ)
