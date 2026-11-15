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
