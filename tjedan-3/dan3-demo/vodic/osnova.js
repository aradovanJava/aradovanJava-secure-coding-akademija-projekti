// Zajedničke pomoćne funkcije za Word vodiče (stil kao vodič za bazu podataka).
const {
  Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType,
  HeadingLevel, LevelFormat, Header, Footer, PageNumber, TabStopType, Tab, LineRuleType, ExternalHyperlink,
} = require("docx");

const PINK = "EE2F58", TAMNA = "1F1F2E", SIVA = "5A5A66", SVIJETLA = "F3F3F6", RUB = "D9D9DE", LINK = "0563C1";
const FONT = "Arial", MONO = "Consolas";
const SIRINA = 9638; // A4, margine 2 cm

// **podebljano**, `kod` i [tekst](https://…) unutar teksta
function runovi(tekst, opcije = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\(https?:[^)\s]+\))/g;
  let zadnji = 0, m;
  while ((m = re.exec(tekst))) {
    if (m.index > zadnji) out.push(new TextRun({ text: tekst.slice(zadnji, m.index), ...opcije }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...opcije }));
    else if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: Math.min(18, (opcije.size || 20) - 2), ...opcije, ...(opcije.bold ? {} : {}) }));
    else {
      const [, txt, url] = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(t);
      out.push(new ExternalHyperlink({ link: url, children: [new TextRun({ text: txt, color: LINK, underline: {}, ...opcije })] }));
    }
    zadnji = m.index + t.length;
  }
  if (zadnji < tekst.length) out.push(new TextRun({ text: tekst.slice(zadnji), ...opcije }));
  return out;
}

const P = (tekst, opcije = {}) => new Paragraph({ children: runovi(tekst), spacing: { after: 120 }, ...opcije });
const H1 = (t, novaStranica = true) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: novaStranica,
  children: [new TextRun(t)], ...(novaStranica ? {} : { spacing: { before: 480, after: 160 } }) });
const H2 = (t, opcije = {}) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)], ...opcije });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const B = (t, razina = 0) => new Paragraph({ numbering: { reference: "tocke", level: razina }, children: runovi(t), spacing: { after: 60 } });
let instanca = 0;
const novaLista = () => ++instanca;
const N = (t, inst) => new Paragraph({ numbering: { reference: "brojevi", level: 0, instance: inst }, children: runovi(t), spacing: { after: 70 } });
// nastavi = true: numeracija se nastavlja na prethodni popis (npr. nakon bloka koda)
const koraci = (popis, nastavi = false) => { const i = nastavi ? instanca : novaLista(); return popis.map((t) => N(t, i)); };

function kod(tekst, naslov) {
  const retci = tekst.split("\n");
  const kratko = retci.length <= 28;
  const p = [];
  if (naslov) p.push(new Paragraph({ keepNext: true, spacing: { before: 120, after: 40 },
    children: [new TextRun({ text: naslov, bold: true, size: 18, color: SIVA })] }));
  retci.forEach((r, i) => {
    const komentar = /^\s*(#|\/\/)/.test(r);
    p.push(new Paragraph({
      keepNext: kratko && i < retci.length - 1, keepLines: true,
      shading: { type: ShadingType.CLEAR, fill: SVIJETLA, color: "auto" },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: PINK, space: 4 } },
      spacing: { before: i === 0 ? 40 : 0, after: i === retci.length - 1 ? 160 : 0, line: r.length ? 252 : 140, lineRule: LineRuleType.AUTO },
      indent: { left: 60 },
      children: [new TextRun({ text: r.length ? r : " ", font: MONO, size: 16, color: komentar ? "6B6B78" : TAMNA })],
    }));
  });
  return p;
}

const rubovi = { top: { style: BorderStyle.SINGLE, size: 4, color: RUB }, bottom: { style: BorderStyle.SINGLE, size: 4, color: RUB },
  left: { style: BorderStyle.SINGLE, size: 4, color: RUB }, right: { style: BorderStyle.SINGLE, size: 4, color: RUB } };

function tablica(zaglavlje, retci, sirine, opcije = {}) {
  const ukupno = sirine.reduce((a, b) => a + b, 0);
  if (ukupno !== SIRINA) throw new Error(`širine tablice ${ukupno} ≠ ${SIRINA}: ${zaglavlje.join(" | ")}`);
  const sz = opcije.velicina || 17;
  const zajedno = opcije.zajedno ?? retci.length <= 8;
  const celija = (t, i, zag, j) => new TableCell({
    width: { size: sirine[i], type: WidthType.DXA }, borders: rubovi,
    shading: zag ? { type: ShadingType.CLEAR, fill: TAMNA, color: "auto" }
      : (j % 2 ? { type: ShadingType.CLEAR, fill: "FAFAFB", color: "auto" } : undefined),
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: String(t).split("\n").map((l) => new Paragraph({
      spacing: { after: 0 }, keepNext: zajedno && (zag || j < retci.length - 1),
      children: zag ? [new TextRun({ text: l, bold: true, color: "FFFFFF", size: sz })]
        : runovi(l, { size: sz, ...(opcije.prviPodebljan && i === 0 ? { bold: true } : {}) }),
    })),
  });
  return new Table({
    width: { size: ukupno, type: WidthType.DXA }, columnWidths: sirine,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: zaglavlje.map((t, i) => celija(t, i, true, 0)) }),
      ...retci.map((r, j) => new TableRow({ cantSplit: true, children: r.map((t, i) => celija(t, i, false, j)) })),
    ],
  });
}

// Okvir s obojenim lijevim rubom. vrsta: "recite" | "pazite" | "ocekivano" | "pitanje" | "info"
const VRSTE = {
  recite: { boja: TAMNA, pozadina: "F1F1F5", naslov: "Recite" },
  pazite: { boja: PINK, pozadina: "FDF2F5", naslov: "Pazite" },
  ocekivano: { boja: "2E7D32", pozadina: "EEF6EF", naslov: "Što se vidi" },
  pitanje: { boja: "8A5A00", pozadina: "FFF7E6", naslov: "Pitanje za polaznike" },
  info: { boja: LINK, pozadina: "EEF4FB", naslov: "Napomena" },
};
function okvir(vrsta, odlomci, naslov) {
  const v = VRSTE[vrsta] || VRSTE.info;
  const bez = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return new Table({
    width: { size: SIRINA, type: WidthType.DXA }, columnWidths: [SIRINA],
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({
      width: { size: SIRINA, type: WidthType.DXA },
      borders: { top: bez, bottom: bez, right: bez, left: { style: BorderStyle.SINGLE, size: 24, color: v.boja } },
      shading: { type: ShadingType.CLEAR, fill: v.pozadina, color: "auto" },
      margins: { top: 90, bottom: 90, left: 180, right: 140 },
      children: [
        new Paragraph({ spacing: { after: 50 }, keepNext: true, children: [new TextRun({ text: naslov || v.naslov, bold: true, color: v.boja, size: 19 })] }),
        ...odlomci.map((t) => new Paragraph({ spacing: { after: 40 }, children: runovi(t, { size: 19 }) })),
      ],
    })] })],
  });
}
const razmak = (n = 80) => new Paragraph({ spacing: { after: n }, children: [] });

function stilovi() {
  return {
    default: { document: { run: { font: FONT, size: 20, color: "222228" }, paragraph: { spacing: { line: 276, lineRule: LineRuleType.AUTO } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: PINK }, paragraph: { spacing: { before: 240, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: TAMNA }, paragraph: { spacing: { before: 280, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 21, bold: true, color: TAMNA }, paragraph: { spacing: { before: 200, after: 80 }, keepNext: true, outlineLevel: 2 } },
    ],
  };
}
function numeracija() {
  return { config: [
    { reference: "tocke", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 260 } } } },
    ] },
    { reference: "brojevi", levels: [
      { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } },
    ] },
  ] };
}
function zaglavlje(tekst) {
  return new Header({ children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: SIRINA }],
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RUB, space: 4 } },
    children: [new TextRun({ text: tekst, size: 16, color: SIVA }), new TextRun({ children: [new Tab(), "SAMO ZA PREDAVAČA"], size: 16, bold: true, color: PINK })],
  })] });
}
function podnozje() {
  return new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ size: 16, color: SIVA, children: ["Stranica ", PageNumber.CURRENT, " od ", PageNumber.TOTAL_PAGES] })] })] });
}

module.exports = { PINK, TAMNA, SIVA, FONT, MONO, SIRINA, runovi, P, H1, H2, H3, B, N, koraci, kod, tablica, okvir, razmak,
  stilovi, numeracija, zaglavlje, podnozje };
