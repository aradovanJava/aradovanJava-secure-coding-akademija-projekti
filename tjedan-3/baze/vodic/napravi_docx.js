// Vodič za predavača – Sigurnost baza podataka (Tjedan 3): Word dokument iz sadrzaj.json.
// node napravi_docx.js sadrzaj.json izlaz.docx
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, HeadingLevel, LevelFormat, Header, Footer, PageNumber, TabStopType, Tab, LineRuleType,
} = require("docx");

const [, , ULAZ, IZLAZ] = process.argv;
const S = JSON.parse(fs.readFileSync(ULAZ, "utf8"));

const PINK = "EE2F58", TAMNA = "1F1F2E", SIVA = "5A5A66", SVIJETLA = "F3F3F6", RUB = "D9D9DE";
const FONT = "Arial", MONO = "Consolas";
const SIRINA = 9638; // A4, margine 2 cm

// ------------------------------------------------------------------ pomoćne funkcije
const runovi = (tekst, opcije = {}) => {
  // **podebljano** i `kod` unutar teksta
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let zadnji = 0, m;
  while ((m = re.exec(tekst))) {
    if (m.index > zadnji) out.push(new TextRun({ text: tekst.slice(zadnji, m.index), ...opcije }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...opcije }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: 18, ...opcije }));
    zadnji = m.index + t.length;
  }
  if (zadnji < tekst.length) out.push(new TextRun({ text: tekst.slice(zadnji), ...opcije }));
  return out;
};
const P = (tekst, opcije = {}) => new Paragraph({ children: runovi(tekst), spacing: { after: 120 }, ...opcije });
const H1 = (t, novaStranica = true) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: novaStranica, children: [new TextRun(t)], ...(novaStranica ? {} : { spacing: { before: 480, after: 160 } }) });
const H2 = (t, opcije = {}) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)], ...opcije });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const B = (t, razina = 0) => new Paragraph({ numbering: { reference: "tocke", level: razina }, children: runovi(t), spacing: { after: 60 } });
const N = (t, ref = "brojevi") => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runovi(t), spacing: { after: 60 } });

function kod(tekst, naslov) {
  const retci = tekst.split("\n");
  const kratko = retci.length <= 28;
  const p = [];
  if (naslov) p.push(new Paragraph({
    keepNext: true, spacing: { before: 120, after: 40 },
    children: [new TextRun({ text: naslov, bold: true, size: 18, color: SIVA })],
  }));
  retci.forEach((r, i) => {
    const komentar = /^\s*--/.test(r) || /^:setvar/.test(r);
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
  const sz = opcije.velicina || 17;
  const zajedno = opcije.zajedno ?? retci.length <= 10; // kratke tablice ne lome se preko stranice
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

function okvir(naslov, odlomci, boja = PINK) {
  return new Table({
    width: { size: SIRINA, type: WidthType.DXA }, columnWidths: [SIRINA],
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({
      width: { size: SIRINA, type: WidthType.DXA },
      borders: { top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
        right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, left: { style: BorderStyle.SINGLE, size: 24, color: boja } },
      shading: { type: ShadingType.CLEAR, fill: "FDF2F5", color: "auto" },
      margins: { top: 100, bottom: 100, left: 180, right: 140 },
      children: [
        new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: naslov, bold: true, color: boja })] }),
        ...odlomci.map((t) => new Paragraph({ spacing: { after: 40 }, children: runovi(t, { size: 19 }) })),
      ],
    })] })],
  });
}
const razmak = () => new Paragraph({ spacing: { after: 80 }, children: [] });

// ------------------------------------------------------------------ sadržaj
const D = [];

// Naslovnica
D.push(
  new Paragraph({ spacing: { before: 2200, after: 120 }, children: [new TextRun({ text: "SECURE CODING AKADEMIJA · TJEDAN 3", bold: true, color: PINK, size: 20 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Sigurnost baza podataka", font: FONT, size: 56, bold: true, color: TAMNA })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Rješenja zadataka Z1–Z8: ranjivosti, ispravci i testovi", size: 32, color: SIVA })] }),
  new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: PINK, space: 4 } }, spacing: { after: 300 }, children: [] }),
  P("Vodič za predavača · SQL Server 2022 u Dockeru · paket „Sigurnost baza podataka”"),
  P("Primjeri su za domenu **MedTermin**; Ulaznica i Kadrovska razlikuju se samo nazivima i pravima aplikacije (poglavlje 5)."),
  P("Stanje: 17. 11. 2026. · Izvor: privatni repozitorij, `tjedan-3/baze/vodic/` i `tjedan-3/baze/rjesenje/`"),
  razmak(),
  okvir("SAMO ZA PREDAVAČA", [
    "Dokument sadrži potpuno rješenje laboratorija i ključ za ocjenjivanje analize Z1. Ne objavljujte ga na Moodleu, ne dijelite ga polaznicima i ne prikazujte ga na projektoru prije roka predaje.",
  ]),
);

// Sadržaj (statičan popis – bez polja koja Word traži osvježiti)
D.push(H1("Sadržaj"));
[
  "1. Kako koristiti vodič",
  "2. Z1 – Prijetnje zatečenog stanja (ključ za ocjenjivanje)",
  "3. Rješenja korak po korak (K1–K9)",
  ...S.KORACI.map((k) => `      ${k.id} · ${k.zadatak} – ${k.naslov}`),
  "4. Završna provjera",
  "5. Razlike po domenama",
  "6. Što rješenje znači za aplikaciju",
  "Dodatak A – Cijelo rješenje jednom naredbom",
  "Dodatak B – Reset na početno stanje",
  "Dodatak C – Česti problemi",
].forEach((t) => D.push(new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: t, size: 21 })] })));

// 1. Kako koristiti
D.push(H1("1. Kako koristiti vodič"));
D.push(P("Vodič prati `ZADACI.md` iz paketa. Za svaku ranjivost navodi gdje nastaje (datoteka i redak u skriptama početnog stanja), kako je ispraviti (T-SQL), kako ispravak provjeriti vlastitim testnim upitom i koji redci automatske provjere tada prelaze u `PROŠLO`."));
D.push(P("SQL je preuzet iz referentnog rješenja (`tjedan-3/baze/rjesenje/medtermin.sql`), podijeljen u devet koraka. Svi koraci i testni upiti iz ovog vodiča izvedeni su redom na svježem SQL Serveru 2022 za sve tri domene (GitHub Actions, workflow `t3-baze-vodic`): nakon svakog koraka prolaze očekivane provjere, a na kraju svih 30 automatskih provjera i demo aplikacije s 0 upozorenja."));

D.push(H2("1.1 Priprema"));
[
  "Iz mape paketa pokrenite poslužitelj: `docker compose up -d` (prvi put pričekajte da `sql` bude `healthy` u `docker compose ps`).",
  "U SSMS-u se spojite kao `sa` (lozinka `MSSQL_SA_PASSWORD` iz `.env`): Server name `tcp:127.0.0.1,1433` (ili port iz `SQL_PORT`), SQL Server Authentication, Encryption Mandatory i uključen Trust server certificate.",
  "Uključite **Query → SQLCMD Mode**. Koraci K2, K5, K7 i K8 počinju naredbama `:setvar` za lozinke; bez SQLCMD načina SSMS ih ne razumije. Primjere lozinki zamijenite svojima (dovoljno složenima za politiku lozinki).",
  "Svaki korak izvedite cijelog (F5) u svom prozoru upita, pa zatim njegov test. `:setvar` vrijedi samo za tekst koji se izvodi – ne označavajte dio skripte bez naredbi `:setvar`.",
  "Polazno stanje provjerite automatskom provjerom: `docker compose --profile provjera run --rm provjera` – gotovo sve provjere javljaju `PALO`.",
].forEach((t) => D.push(N(t)));

D.push(H2("1.2 Redoslijed izvođenja"));
D.push(P("Redoslijed je provjeren u CI-ju. Revizija je prva (bilježi sve što slijedi), očvršćivanje rano (zatvara najopasnije putove), šifriranje stupca prije RLS-a (mijenja strukturu tablice), a `sa` se gasi tek na kraju."));
D.push(tablica(["Korak", "Zadatak", "Što se radi", "Provjere → PROŠLO"],
  S.KORACI.map((k) => [k.id, k.zadatak, k.naslov, k.provjere.join(", ")]),
  [900, 1300, 4438, 3000], { prviPodebljan: true }));
D.push(razmak());
D.push(okvir("Automatska provjera nakon svakog koraka", [
  "`docker compose --profile provjera run --rm provjera` – ispis ima jedan redak po provjeri (`PROŠLO`/`PALO`) sa savjetom i na kraju strojno čitljive retke `REZULTAT|Z3.2|PROŠLO`.",
  "Provjera ne mijenja bazu; izvodi samo nekoliko SELECT upita u ime aplikacije i podrške (vidjet ćete ih u reviziji).",
  "Nakon K9 (sa onemogućen) provjera radi tek kad su `ADMIN_LOGIN` i `ADMIN_PASSWORD` upisani u `.env` i pokrenut `docker compose up -d`.",
], TAMNA));

// 2. Z1
D.push(H1("2. Z1 – Prijetnje zatečenog stanja"));
D.push(P("Z1 je pisani zadatak: polaznik istražuje zatečeno stanje upitima nad katalogom i predaje barem 8 prijetnji – što je pronašao (upit i rezultat), kako bi se to zloupotrijebilo i kojim zadatkom (Z2–Z8) se rješava. Upiti u 2.1 su polazište istraživanja, a tablica u 2.2 ključ za ocjenjivanje; uzroci su u `skripte/postavljanje/zatecene-postavke.sql` i `skripte/postavljanje/medtermin.sql`."));
D.push(H2("2.1 Upiti za istraživanje (sistemski katalog)"));
D.push(P("Pogledi `sys.*` nisu datoteke u paketu nego ugrađeni katalog SQL Servera; čitaju se običnim SELECT-om. Prazan rezultat je također nalaz (nema TDE-a, kopija ni revizije). Pogledi `sys.database_*` vrijede za trenutačno odabranu bazu."));
kod(`-- Prijave i politika lozinki
SELECT name, type_desc, is_disabled, create_date
FROM sys.server_principals
WHERE type IN ('S', 'U', 'G') AND name NOT LIKE '##%';
SELECT name, is_policy_checked, is_expiration_checked, is_disabled
FROM sys.sql_logins WHERE name NOT LIKE '##%';

-- Članstvo u ulogama poslužitelja
SELECT r.name AS uloga, m.name AS clan
FROM sys.server_role_members rm
JOIN sys.server_principals r ON r.principal_id = rm.role_principal_id
JOIN sys.server_principals m ON m.principal_id = rm.member_principal_id;

-- Baze: vlasnik, TRUSTWORTHY, šifriranje
SELECT name, SUSER_SNAME(owner_sid) AS vlasnik, is_trustworthy_on, is_encrypted, recovery_model_desc
FROM sys.databases;

-- Opasne postavke poslužitelja
SELECT name, value_in_use FROM sys.configurations
WHERE name IN ('xp_cmdshell', 'clr enabled', 'Ole Automation Procedures',
               'cross db ownership chaining', 'Ad Hoc Distributed Queries');

-- TDE, kopije, revizija
SELECT DB_NAME(database_id) AS baza, encryption_state, encryptor_type FROM sys.dm_database_encryption_keys;
SELECT database_name, type, backup_finish_date, key_algorithm
FROM msdb.dbo.backupset ORDER BY backup_finish_date DESC;
SELECT name, type_desc, is_state_enabled FROM sys.server_audits;

-- Unutar baze domene: uloge i dozvole (uključujući public i guest)
USE MedTermin;
SELECT r.name AS uloga, m.name AS clan
FROM sys.database_role_members rm
JOIN sys.database_principals r ON r.principal_id = rm.role_principal_id
JOIN sys.database_principals m ON m.principal_id = rm.member_principal_id;
SELECT pr.name AS korisnik, pe.state_desc, pe.permission_name, pe.class_desc,
       CASE WHEN pe.class = 1 THEN OBJECT_NAME(pe.major_id) END AS objekt
FROM sys.database_permissions pe
JOIN sys.database_principals pr ON pr.principal_id = pe.grantee_principal_id
WHERE pr.name IN ('public', 'guest') OR pr.type IN ('S', 'U');`).forEach((p) => D.push(p));
D.push(H2("2.2 Ključ za ocjenjivanje: 14 prijetnji"));
D.push(tablica(["#", "Prijetnja i nalaz u katalogu", "Uzrok", "Scenarij zlouporabe", "Ispravak"],
  S.Z1.map((r) => [r[0], `**${r[1]}**\n${r[2]}`, r[3], r[4], r[5]]),
  [380, 2450, 1650, 3900, 1258], { velicina: 16 }));
D.push(H2("2.3 Kombinacije – što razlikuje dobru analizu od popisa"));
S.KOMBINACIJE.forEach(([n, t]) => D.push(B(`**${n}:** ${t}`)));

// 3. Koraci
D.push(H1("3. Rješenja korak po korak", false));
D.push(P("Svaki korak ima isti raspored: koje provjere rješava i gdje je uzrok, što napraviti i zašto, T-SQL za MedTermin, testni upit kojim se vidi da je ranjivost otklonjena, očekivani rezultat i – gdje ih `ZADACI.md` postavlja – odgovore na pitanja za razmišljanje."));
S.KORACI.forEach((k, idx) => {
  D.push(H2(`${k.id} · ${k.zadatak} – ${k.naslov}`, idx > 0 ? { spacing: { before: 480, after: 120 } } : {}));
  D.push(tablica(["Provjere", "Uzrok ranjivosti"], [[k.provjere.join(", "), k.uzrok]], [1900, 7738], { velicina: 18 }));
  D.push(H3("Što napraviti i zašto"));
  k.zasto.forEach((t) => D.push(B(t)));
  kod(k.sql.replace("{PRAVA}", S.PRAVA.medtermin), "T-SQL (MedTermin)").forEach((p) => D.push(p));
  D.push(H3("Test: je li ranjivost otklonjena"));
  kod(k.test).forEach((p) => D.push(p));
  if (k.test_medtermin) kod(k.test_medtermin, "Dodatni test (samo MedTermin – stupci glavne tablice razlikuju se po domeni)").forEach((p) => D.push(p));
  D.push(new Paragraph({ keepNext: true, spacing: { before: 60, after: 60 }, children: [new TextRun({ text: "Očekivani rezultat", bold: true, color: TAMNA })] }));
  k.ocekivano.forEach((t) => D.push(B(t)));
  D.push(P(`**Automatska provjera:** nakon ovog koraka u ispisu provjere retci ${k.provjere.join(", ")} javljaju \`PROŠLO\` (i svi iz prethodnih koraka ostaju \`PROŠLO\`).`, { spacing: { before: 80, after: 120 } }));
  if (k.pitanje) {
    D.push(okvir(`Pitanje iz ZADACI.md: ${k.pitanje[0]}`, [k.pitanje[1]], TAMNA));
    D.push(razmak());
  }
  if (k.id === "K1") D.push(okvir("Ako Z6.5 javi PALO", ["Zapisi se u datoteku upisuju s kratkom odgodom (QUEUE_DELAY). Pokrenite provjeru još jednom – CI je u tom slučaju ponavlja nakon tri sekunde."], TAMNA));
  if (k.id === "K6") D.push(okvir("Provjera iz aplikacije", ["Nakon ovog koraka riješeni su Z2–Z4 (osim gašenja sa). U `.env` upišite `APP_LOZINKA` (nova lozinka iz K2) i pokrenite demo: `docker compose --profile aplikacija run --rm aplikacija-python` (ili `-java`, `-dotnet`). Ispis mora završiti s `Upozorenja: 0` – u početnom stanju bilo ih je 12."], TAMNA));
});

// 4. Završna provjera
D.push(H1("4. Završna provjera", false));
D.push(P("Nakon K9 u `.env` upišite administratorsku prijavu i novu lozinku aplikacije (vrijednosti iz K2), pa ponovno pokrenite poslužitelj, provjeru i demo:"));
kod(S.ZAVRSNO.env, ".env").forEach((p) => D.push(p));
kod(S.ZAVRSNO.naredbe, "PowerShell, u mapi paketa").forEach((p) => D.push(p));
D.push(P("Očekivano:"));
[
  "Svih 30 automatskih provjera (Z2.1–Z8.3) javlja `PROŠLO`.",
  "Demo aplikacije završava s `Upozorenja: 0` – isti rezultat u Pythonu, Javi i C#-u.",
  "Za predaju polaznik prilaže ispis: `docker compose --profile provjera run --rm provjera > provjera.txt`.",
].forEach((t) => D.push(B(t)));
D.push(okvir("Kriterij za predaju (ZADACI.md)", [
  "Skripta (ili numerirane skripte) mora na svježoj bazi dovesti sve automatske provjere u PROŠLO – bez lozinki upisanih u skriptu (sqlcmd varijable ili ručni unos).",
  "Uz skriptu: ispis provjere, pisana analiza Z1 (barem 8 prijetnji s upitom, scenarijem i zadatkom) i kratki odgovori na pitanja iz zadataka (najviše 2 stranice).",
], TAMNA));

// 5. Domene
D.push(H1("5. Razlike po domenama", false));
D.push(P("SQL u vodiču je za MedTermin. Za ostale domene zamijenite nazive prema tablici; jedino se razlikuje blok prava aplikacije u K3 (prava odgovaraju upitima T2 aplikacije te domene).", { keepNext: true }));
D.push(tablica(["", "MedTermin", "Ulaznica", "Kadrovska"], [
  ["Baza", "MedTermin", "Ulaznica", "Kadrovska"],
  ["Aplikacijska prijava i korisnik", "medtermin_app", "ulaznica_app", "kadrovska_app"],
  ["Glavna tablica", "rezervacije", "narudzbe", "zahtjevi"],
  ["Stupac vlasnika", "pacijent", "kupac", "zaposlenik"],
  ["Druga osjetljiva tablica", "nalazi", "racuni", "platne_liste"],
  ["Sigurnosna politika (K6)", "politika_rezervacije", "politika_narudzbe", "politika_zahtjevi"],
  ["TDE certifikat, audit, kopija", "CertTDE_MedTermin,\nRevizija_MedTermin,\nMedTermin_puna.bak", "CertTDE_Ulaznica,\nRevizija_Ulaznica,\nUlaznica_puna.bak", "CertTDE_Kadrovska,\nRevizija_Kadrovska,\nKadrovska_puna.bak"],
], [2600, 2346, 2346, 2346], { prviPodebljan: true }));
D.push(H2("5.1 Prava aplikacije u K3 – Ulaznica"));
kod(S.PRAVA.ulaznica).forEach((p) => D.push(p));
D.push(H2("5.2 Prava aplikacije u K3 – Kadrovska"));
kod(S.PRAVA.kadrovska).forEach((p) => D.push(p));
D.push(P("Testni upiti vrijede za sve domene uz iste zamjene; dodatni testovi u K3 i K6 (upis u glavnu tablicu) napisani su samo za MedTermin jer se stupci glavne tablice razlikuju."));

// 6. Aplikacija
D.push(H1("6. Što rješenje znači za aplikaciju", false));
D.push(P("Laboratorij se radi na strani baze, ali dva ispravka mijenjaju način na koji aplikacija mora raditi – dobra točka za raspravu s polaznicima („sigurnost baze nije samo posao DBA-e”):"));
[
  "**Šifrirani OIB (K5):** upis ide preko `OPEN SYMMETRIC KEY KljucOib DECRYPTION BY CERTIFICATE CertOib` i `ENCRYPTBYKEY(KEY_GUID(N'KljucOib'), @oib)`, čitanje preko `CONVERT(VARCHAR(11), DECRYPTBYKEYAUTOCERT(CERT_ID(N'CertOib'), NULL, oib_sifrirano))`. T2 aplikacija bez te izmjene ne zna upisati ni pročitati OIB rezervacije.",
  "**RLS (K6):** nakon prijave korisnika aplikacija na istoj konekciji poziva `EXEC sp_set_session_context @key = N'korisnik', @value = N'ana', @read_only = 1;`. Bez toga aplikacija ne vidi nijednu rezervaciju (bez konteksta predikat ne vraća ništa). S connection poolingom kontekst se postavlja pri svakom preuzimanju konekcije iz poola.",
  "**Najmanje ovlasti (K3):** promjene sheme (migracije) više ne idu aplikacijskom prijavom nego zasebnom prijavom za migracije ili administratorom – aplikacija nema DDL prava.",
  "**Maskiranje (K6):** aplikacija dobiva granularni UNMASK samo na `dbo.korisnici`; podrška vidi maskirane podatke i ne može čitati `password_hash`.",
].forEach((t) => D.push(B(t)));

// Dodaci
D.push(H1("Dodatak A – Cijelo rješenje jednom naredbom"));
D.push(P("Za brzu demonstraciju ili provjeru: referentno rješenje iz privatnog repozitorija izvodi se na svježoj bazi jednom sqlcmd naredbom unutar kontejnera (PowerShell, iz mape `tjedan-3\\baze` repozitorija ili mape paketa u koju ste kopirali datoteku):"));
kod(`docker compose cp rjesenje/medtermin.sql sql:/tmp/rjesenje.sql
docker compose exec sql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P '<sa lozinka>' \`
    -b -I -f 65001 -i /tmp/rjesenje.sql \`
    -v APP_LOZINKA='<nova lozinka aplikacije>' ADMIN_LOZINKA='<lozinka dba_admin>' \`
       KLJUC_LOZINKA='<lozinka ključeva>'`, "PowerShell").forEach((p) => D.push(p));
D.push(P("Zatim u `.env` postavite `ADMIN_LOGIN=dba_admin`, `ADMIN_PASSWORD` i `APP_LOZINKA` te pokrenite `docker compose up -d` i provjeru. Referentno rješenje ima drukčiji redoslijed od ovog vodiča (revizija dolazi kasnije), ali isti krajnji rezultat; i ono se provjerava u CI-ju (workflow `t3-baze`)."));

D.push(H1("Dodatak B – Reset na početno stanje", false));
kod(`docker compose exec sql sh -c 'rm -f /var/opt/mssql/backup/* /var/opt/mssql/audit/*'
docker compose down -v
docker compose up -d`, "PowerShell, u mapi paketa").forEach((p) => D.push(p));
D.push(P("`down -v` briše volumen s bazom i sve promjene. Datoteke certifikata u `backup\\` moraju se obrisati prije ponovnog izvođenja K7 i K8 (inače `BACKUP CERTIFICATE` javlja da datoteka već postoji). Na Windowsu ih možete obrisati i iz Explorera. Nakon reseta vrijede `sa` i lozinka iz `.env`; `ADMIN_LOGIN` i `ADMIN_PASSWORD` u `.env` vratite na prazno."));

D.push(H1("Dodatak C – Česti problemi", false));
D.push(tablica(["Simptom", "Uzrok i rješenje"], [
  ["Docker: „ports are not available … 1433 … forbidden by its access permissions”", "Na računalu radi SQL Server (servis MSSQLSERVER) ili je Windows rezervirao port. U `.env` postavite `SQL_PORT=14333` i spajajte se na `tcp:127.0.0.1,14333`, ili zaustavite lokalni servis (PowerShell kao administrator: `Stop-Service MSSQLSERVER -Force`)."],
  ["SSMS se ne može spojiti na kontejner", "Server name `tcp:127.0.0.1,<port>` (zarez, ne dvotočka); SQL Server Authentication; Trust server certificate. Kontejner mora biti `healthy` (`docker compose ps`)."],
  ["Lozinka iz `.env` ne prolazi za sa", "Lozinka se postavlja samo pri prvom stvaranju volumena; nakon promjene `.env` vrijedi stara. Reset (dodatak B)."],
  ["„Incorrect syntax near ':'” u SSMS-u", "Nije uključen Query → SQLCMD Mode (naredbe `:setvar`)."],
  ["K7/K8: datoteka certifikata već postoji", "Ostatak prethodnog pokušaja u `backup\\` – obrišite datoteke (dodatak B)."],
  ["Z6.5 PALO odmah nakon K1", "Zapisi revizije kasne sekundu-dvije; pokrenite provjeru ponovno."],
  ["Provjera nakon K9: „ne mogu se prijaviti … kao 'sa'”", "U `.env` upišite `ADMIN_LOGIN=dba_admin` i `ADMIN_PASSWORD`, pa `docker compose up -d`."],
  ["Demo: „Ne mogu se spojiti kao medtermin_app”", "Lozinka aplikacije promijenjena je u K2 – upišite je u `.env` kao `APP_LOZINKA`."],
], [3400, 6238]));

// ------------------------------------------------------------------ dokument
const doc = new Document({
  creator: "Secure Coding akademija",
  title: "Sigurnost baza podataka – rješenja zadataka Z1–Z8",
  description: "Vodič za predavača – samo za predavača",
  styles: {
    default: { document: { run: { font: FONT, size: 20, color: "222228" }, paragraph: { spacing: { line: 276, lineRule: LineRuleType.AUTO } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: PINK },
        paragraph: { spacing: { before: 240, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: TAMNA },
        paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 21, bold: true, color: TAMNA },
        paragraph: { spacing: { before: 180, after: 80 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "tocke", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 260 } } } },
      ] },
      { reference: "brojevi", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } },
      ] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134, header: 567, footer: 567 } } },
    headers: { default: new Header({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: SIRINA }],
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RUB, space: 4 } },
      children: [
        new TextRun({ text: "Sigurnost baza podataka · rješenja Z1–Z8", size: 16, color: SIVA }),
        new TextRun({ children: [new Tab(), "SAMO ZA PREDAVAČA"], size: 16, bold: true, color: PINK }),
      ] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ size: 16, color: SIVA, children: ["Stranica ", PageNumber.CURRENT, " od ", PageNumber.TOTAL_PAGES] })] })] }) },
    children: D,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(IZLAZ, buf); console.log("spremljeno:", IZLAZ, buf.length); });
