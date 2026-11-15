"""Pomoćne funkcije za uređivanje Span prezentacija (python-pptx + lxml, bez gubitka formatiranja)."""
import copy

from lxml import etree
from pptx.oxml.ns import qn

A = "http://schemas.openxmlformats.org/drawingml/2006/main"

KOD = "F2F2F2"
ISTAKNUTO = "FF8FA8"
KOMENTAR = "9A9AA6"
PINK = "EE2F58"
OZNAKA_SIVO = "C8C8D0"


def oblik(slide, shape_id):
    for sh in slide.shapes:
        if sh.shape_id == shape_id:
            return sh
    raise KeyError(f"shape {shape_id} nije na slajdu")


def _run(tekst, sz, b, boja, font):
    r = etree.SubElement(etree.Element(qn("a:p")), qn("a:r"))
    rpr = etree.SubElement(r, qn("a:rPr"), sz=str(sz), b="1" if b else "0")
    fill = etree.SubElement(rpr, qn("a:solidFill"))
    etree.SubElement(fill, qn("a:srgbClr"), val=boja)
    etree.SubElement(rpr, qn("a:latin"), typeface=font)
    t = etree.SubElement(r, qn("a:t"))
    t.text = tekst
    return r


def postavi_kod(shape, retci, sz=None):
    """Zamijeni sadržaj tekstnog okvira s kodom. Redak: str ili (str, 'h'|'c') – istaknuto / komentar."""
    tx = shape.text_frame._txBody
    stari = tx.findall(qn("a:p"))
    predlozak = copy.deepcopy(stari[0])
    prvi_run = predlozak.find(qn("a:r"))
    if sz is None:
        sz = int(prvi_run.find(qn("a:rPr")).get("sz")) if prvi_run is not None else 860
    for p in stari:
        tx.remove(p)
    for redak in retci:
        tekst, vrsta = (redak, "n") if isinstance(redak, str) else redak
        p = copy.deepcopy(predlozak)
        for el in list(p):
            if el.tag != qn("a:pPr"):
                p.remove(el)
        boja = {"n": KOD, "h": ISTAKNUTO, "c": KOMENTAR}[vrsta]
        p.append(_run(tekst if tekst else " ", sz, vrsta == "h", boja, "Consolas"))
        tx.append(p)


def postavi_oznaku(shape, jezik, opis):
    """Oznaka iznad koda: 'Java  ' (pink, bold) + opis (sivo)."""
    tx = shape.text_frame._txBody
    p = tx.find(qn("a:p"))
    runs = p.findall(qn("a:r"))
    if len(runs) == 1:  # oznaka s jednim runom (npr. „tajne u razvoju”)
        runs[0].find(qn("a:t")).text = f"{opis} ({jezik})"
        return
    runs[0].find(qn("a:t")).text = jezik + "  "
    if len(runs) > 1:
        runs[1].find(qn("a:t")).text = opis
        for r in runs[2:]:
            p.remove(r)


def zamijeni_tekst(slide, staro, novo, obavezno=True):
    """Zamjena unutar jednog runa (čuva formatiranje). Vraća broj zamjena."""
    n = 0
    for sh in slide.shapes:
        if sh.has_text_frame:
            okviri = [sh.text_frame]
        elif getattr(sh, "has_table", False) and sh.has_table:
            okviri = [c.text_frame for r in sh.table.rows for c in r.cells]
        else:
            continue
        for tf in okviri:
            for p in tf.paragraphs:
                for r in p.runs:
                    if staro in r.text:
                        r.text = r.text.replace(staro, novo)
                        n += 1
    if obavezno and n == 0:
        raise ValueError(f"nije pronađeno: {staro!r}")
    return n


def postavi_odlomke(shape, odlomci, predlozak_naslova=0, predlozak_stavke=1):
    """Tekstni okvir 'naslov + stavke': odlomci = [naslov, stavka, stavka …] (kopira formatiranje postojećih)."""
    tx = shape.text_frame._txBody
    stari = tx.findall(qn("a:p"))
    tn = copy.deepcopy(stari[predlozak_naslova])
    ts = copy.deepcopy(stari[min(predlozak_stavke, len(stari) - 1)])
    for p in stari:
        tx.remove(p)
    for i, tekst in enumerate(odlomci):
        p = copy.deepcopy(tn if i == 0 else ts)
        runs = p.findall(qn("a:r"))
        runs[0].find(qn("a:t")).text = tekst
        for r in runs[1:]:
            p.remove(r)
        tx.append(p)


def postavi_odlomke_s_oznakom(shape, retci):
    """Okvir čiji odlomci imaju dva runa (oznaka + tekst): retci = [(oznaka, tekst), …]; kopira prvi odlomak."""
    tx = shape.text_frame._txBody
    stari = tx.findall(qn("a:p"))
    predlozak = copy.deepcopy(stari[0])
    zadnji = copy.deepcopy(stari[-1])
    for p in stari:
        tx.remove(p)
    for i, (oznaka, tekst) in enumerate(retci):
        p = copy.deepcopy(zadnji if i == len(retci) - 1 else predlozak)
        runs = p.findall(qn("a:r"))
        runs[0].find(qn("a:t")).text = oznaka
        runs[1].find(qn("a:t")).text = tekst
        for r in runs[2:]:
            p.remove(r)
        tx.append(p)


def biljeske(slide, tekst):
    tf = slide.notes_slide.notes_text_frame
    tf.text = tekst.strip()


# ---------------------------------------------------------------- tablice
def _tekst_celije(tc, tekst, bold=None):
    txb = tc.find(qn("a:txBody"))
    ps = txb.findall(qn("a:p"))
    p0 = ps[0]
    for p in ps[1:]:
        txb.remove(p)
    runs = p0.findall(qn("a:r"))
    if not runs:
        r = etree.SubElement(p0, qn("a:r"))
        etree.SubElement(r, qn("a:rPr"), sz="900")
        etree.SubElement(r, qn("a:t"))
        runs = [r]
    for r in runs[1:]:
        p0.remove(r)
    end = p0.find(qn("a:endParaRPr"))
    if end is not None:
        p0.remove(end)
    runs[0].find(qn("a:t")).text = tekst
    if bold is not None:
        runs[0].find(qn("a:rPr")).set("b", "1" if bold else "0")


def postavi_tablicu(shape, redci, sirine=None, podebljaj_prvi_stupac=False, sz=None):
    """redci[0] = zaglavlje. Broj stupaca i redaka prilagođava se kloniranjem postojećih (čuva stil)."""
    tbl = shape.table._tbl
    grid = tbl.find(qn("a:tblGrid"))
    cols = grid.findall(qn("a:gridCol"))
    trs = tbl.findall(qn("a:tr"))
    n_st = len(redci[0])
    # stupci
    while len(cols) < n_st:
        novi = copy.deepcopy(cols[-1]); grid.append(novi); cols.append(novi)
        for tr in trs:
            tr.append(copy.deepcopy(tr.findall(qn("a:tc"))[-1]))
    while len(cols) > n_st:
        grid.remove(cols.pop())
        for tr in trs:
            tr.remove(tr.findall(qn("a:tc"))[-1])
    # retci (predložak za nove: zadnji podatkovni redak)
    predlozak = copy.deepcopy(trs[2] if len(trs) > 2 else trs[-1])
    while len(trs) < len(redci):
        novi = copy.deepcopy(predlozak); tbl.append(novi); trs.append(novi)
    while len(trs) > len(redci):
        tbl.remove(trs.pop())
    # širine – uvijek ukupno koliko je širok okvir tablice
    ukupno = int(shape.width)
    if not sirine:
        sirine = [int(c.get("w")) for c in cols]
    s = sum(sirine)
    for c, w in zip(cols, sirine):
        c.set("w", str(int(ukupno * w / s)))
    # tekst
    for i, (tr, red) in enumerate(zip(trs, redci)):
        for j, (tc, tekst) in enumerate(zip(tr.findall(qn("a:tc")), red)):
            b = None
            if isinstance(tekst, tuple):
                tekst, b = tekst
            elif podebljaj_prvi_stupac and j == 0 and i > 0:
                b = True
            _tekst_celije(tc, tekst, b)
            if sz and i > 0:
                tc.find(qn("a:txBody")).find(qn("a:p")).find(qn("a:r")).find(qn("a:rPr")).set("sz", str(sz))


# ---------------------------------------------------------------- ikone
ASVG = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
RT_IMAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"


def _svg_blip(pic):
    return pic._element.find(".//{%s}svgBlip" % ASVG)


def ikone_po_imenu(prs):
    """{ime ikone: (slide, pic)} iz svih slajdova (naziv oblika 'Ikona <ime>')."""
    out = {}
    for s in prs.slides:
        for sh in s.shapes:
            if sh.shape_type == 13 and sh.name.startswith("Ikona "):
                out.setdefault(sh.name[6:], (s, sh))
    return out


def zamijeni_ikonu(slide, pic, izvor):
    """Postavi na `pic` (slajd `slide`) sliku iz izvora (slide, pic) – kopira odnos prema istom SVG dijelu."""
    src_slide, src_pic = izvor
    rid = _svg_blip(src_pic).get(qn("r:embed"))
    part = src_slide.part.related_part(rid)
    novi = slide.part.relate_to(part, RT_IMAGE)
    _svg_blip(pic).set(qn("r:embed"), novi)
    ime = src_pic.name[6:]
    pic._element.find(qn("p:nvPicPr")).find(qn("p:cNvPr")).set("name", "Ikona " + ime)
    pic._element.find(qn("p:nvPicPr")).find(qn("p:cNvPr")).set("descr", "Ikona: " + ime)


def obrisi_oblik(shape):
    el = shape._element
    el.getparent().remove(el)


def postavi_tekst(shape, tekst):
    """Prvi run prvog odlomka dobiva tekst; ostali runovi i odlomci se brišu (formatiranje ostaje)."""
    tx = shape.text_frame._txBody
    ps = tx.findall(qn("a:p"))
    for p in ps[1:]:
        tx.remove(p)
    runs = ps[0].findall(qn("a:r"))
    runs[0].find(qn("a:t")).text = tekst
    for r in runs[1:]:
        ps[0].remove(r)


def postavi_retke(shape, retci):
    """Okvir s više odlomaka istog stila (svaki odlomak jedan run): retci = [tekst, …] (kopira prvi odlomak)."""
    tx = shape.text_frame._txBody
    ps = tx.findall(qn("a:p"))
    predlozak = copy.deepcopy(ps[0])
    for p in ps:
        tx.remove(p)
    for t in retci:
        p = copy.deepcopy(predlozak)
        runs = p.findall(qn("a:r"))
        runs[0].find(qn("a:t")).text = t
        for r in runs[1:]:
            p.remove(r)
        tx.append(p)
