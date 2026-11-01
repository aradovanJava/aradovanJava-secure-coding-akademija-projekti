namespace MedTermin.Api.Infrastruktura;

/// <summary>Shema i početni podaci poliklinike: liječnici, termini, rezervacije i nalazi.</summary>
public static class PocetniPodaci
{
    public const string Shema = """
        CREATE TABLE lijecnici (
            id              INTEGER PRIMARY KEY,
            ime             TEXT NOT NULL,
            prezime         TEXT NOT NULL,
            specijalizacija TEXT NOT NULL,
            ordinacija      TEXT NOT NULL
        );

        CREATE TABLE termini (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            lijecnik_id INTEGER NOT NULL REFERENCES lijecnici(id),
            pocetak     TEXT NOT NULL,
            kapacitet   INTEGER NOT NULL,
            zauzeto     INTEGER NOT NULL DEFAULT 0,
            napomena    TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE rezervacije (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            termin_id INTEGER NOT NULL REFERENCES termini(id),
            pacijent  TEXT NOT NULL,
            napomena  TEXT NOT NULL,
            oib       TEXT NOT NULL,
            kreirano  TEXT NOT NULL
        );

        CREATE TABLE nalazi (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            pacijent TEXT NOT NULL,
            naziv    TEXT NOT NULL,
            datoteka TEXT NOT NULL
        );
        """;

    public static void Unesi(Baza baza)
    {
        const string lijecnik = "INSERT INTO lijecnici (id, ime, prezime, specijalizacija, ordinacija) VALUES ($id, $i, $p, $s, $o)";
        baza.Izvrsi(lijecnik, ("$id", 1), ("$i", "Ivan"), ("$p", "Horvat"), ("$s", "Kardiologija"), ("$o", "Ordinacija 101"));
        baza.Izvrsi(lijecnik, ("$id", 2), ("$i", "Maja"), ("$p", "Kovačević"), ("$s", "Dermatologija"), ("$o", "Ordinacija 102"));
        baza.Izvrsi(lijecnik, ("$id", 3), ("$i", "Petra"), ("$p", "Babić"), ("$s", "Neurologija"), ("$o", "Ordinacija 201"));
        baza.Izvrsi(lijecnik, ("$id", 4), ("$i", "Tomislav"), ("$p", "Jurić"), ("$s", "Ortopedija"), ("$o", "Ordinacija 202"));
        baza.Izvrsi(lijecnik, ("$id", 5), ("$i", "Lucija"), ("$p", "Novak"), ("$s", "Oftalmologija"), ("$o", "Ordinacija 203"));
        baza.Izvrsi(lijecnik, ("$id", 6), ("$i", "Damir"), ("$p", "Perić"), ("$s", "Interna medicina"), ("$o", "Ordinacija 301"));

        const string termin = "INSERT INTO termini (id, lijecnik_id, pocetak, kapacitet, zauzeto, napomena) VALUES ($id, $l, $p, $k, $z, $n)";
        baza.Izvrsi(termin, ("$id", 1), ("$l", 1), ("$p", "2026-11-23T09:00"), ("$k", 1), ("$z", 1), ("$n", "Kontrola"));
        baza.Izvrsi(termin, ("$id", 2), ("$l", 1), ("$p", "2026-11-23T10:00"), ("$k", 1), ("$z", 1), ("$n", "Prvi pregled"));
        baza.Izvrsi(termin, ("$id", 3), ("$l", 2), ("$p", "2026-11-24T09:00"), ("$k", 1), ("$z", 0), ("$n", ""));
        baza.Izvrsi(termin, ("$id", 4), ("$l", 2), ("$p", "2026-11-24T09:30"), ("$k", 1), ("$z", 0), ("$n", ""));
        baza.Izvrsi(termin, ("$id", 5), ("$l", 3), ("$p", "2026-11-25T11:00"), ("$k", 1), ("$z", 0), ("$n", ""));
        baza.Izvrsi(termin, ("$id", 6), ("$l", 4), ("$p", "2026-11-25T12:00"), ("$k", 1), ("$z", 0), ("$n", ""));
        baza.Izvrsi(termin, ("$id", 7), ("$l", 5), ("$p", "2026-11-26T08:00"), ("$k", 1), ("$z", 0), ("$n", "Zadnji slobodni termin u tjednu"));
        baza.Izvrsi(termin, ("$id", 8), ("$l", 6), ("$p", "2026-11-26T13:00"), ("$k", 1), ("$z", 0), ("$n", ""));
        baza.Izvrsi(termin, ("$id", 9), ("$l", 1), ("$p", "2026-11-27T14:00"), ("$k", 3), ("$z", 0), ("$n", "Grupno savjetovanje"));
        baza.Izvrsi(termin, ("$id", 10), ("$l", 3), ("$p", "2026-11-27T15:00"), ("$k", 1), ("$z", 0), ("$n", ""));

        const string rezervacija = "INSERT INTO rezervacije (id, termin_id, pacijent, napomena, oib, kreirano) VALUES ($id, $t, $p, $n, $o, $k)";
        baza.Izvrsi(rezervacija, ("$id", 1), ("$t", 1), ("$p", "ana"), ("$n", "Kontrolni pregled tlaka"), ("$o", "48291736504"), ("$k", "2026-11-02T08:15:00Z"));
        baza.Izvrsi(rezervacija, ("$id", 2), ("$t", 2), ("$p", "marko"), ("$n", "Bolovi u leđima"), ("$o", "73019485267"), ("$k", "2026-11-02T09:40:00Z"));

        const string nalaz = "INSERT INTO nalazi (id, pacijent, naziv, datoteka) VALUES ($id, $p, $n, $d)";
        baza.Izvrsi(nalaz, ("$id", 1), ("$p", "ana"), ("$n", "Krvna slika"), ("$d", "nalaz-ana-krvna-slika.txt"));
        baza.Izvrsi(nalaz, ("$id", 2), ("$p", "marko"), ("$n", "RTG kralježnice"), ("$d", "nalaz-marko-rtg.txt"));
    }

    /// <summary>Datoteke nalaza koje se pri pokretanju stvaraju u mapi s dokumentima.</summary>
    public static readonly IReadOnlyDictionary<string, string> Dokumenti = new Dictionary<string, string>
    {
        ["nalaz-ana-krvna-slika.txt"] = """
            POLIKLINIKA MEDTERMIN
            Nalaz: Krvna slika
            Pacijent: Ana Anić
            Datum: 2026-10-15

            Hemoglobin: 138 g/L (ref. 119-157)
            Leukociti: 6.2 x10^9/L (ref. 3.4-9.7)
            Trombociti: 245 x10^9/L (ref. 158-424)

            Zaključak: nalaz uredan.
            Liječnik: dr. Ivan Horvat
            """,
        ["nalaz-marko-rtg.txt"] = """
            POLIKLINIKA MEDTERMIN
            Nalaz: RTG kralježnice
            Pacijent: Marko Marić
            Datum: 2026-10-20

            Opis: lumbalna kralježnica bez znakova svježih koštanih lezija.
            Blago suženje intervertebralnog prostora L4-L5.

            Preporuka: fizikalna terapija, kontrola za 3 mjeseca.
            Liječnik: dr. Tomislav Jurić
            """,
    };
}
