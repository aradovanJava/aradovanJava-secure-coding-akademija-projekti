CREATE TABLE korisnici (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email         TEXT,
    ime           TEXT,
    prezime       TEXT,
    uloga         TEXT NOT NULL,
    oib           TEXT
);

CREATE TABLE reset_tokeni (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL,
    token      TEXT    NOT NULL,
    istjece    TEXT,
    iskoristen INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE postavke (
    username   TEXT PRIMARY KEY,
    podsjetnik INTEGER NOT NULL,
    sati_prije INTEGER NOT NULL,
    kanal      TEXT    NOT NULL
);

-- Cijene i iznosi u eurima s dvije decimale (NUMERIC: sortiranje po vrijednosti, ne po tekstu).
CREATE TABLE dogadjaji (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv     TEXT    NOT NULL,
    mjesto    TEXT    NOT NULL,
    datum     TEXT    NOT NULL,
    cijena    NUMERIC NOT NULL,
    kapacitet INTEGER NOT NULL,
    prodano   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE narudzbe (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    dogadjaj_id     INTEGER NOT NULL REFERENCES dogadjaji (id),
    kupac           TEXT    NOT NULL,
    kolicina        INTEGER NOT NULL,
    ime_na_ulaznici TEXT    NOT NULL,
    oib             TEXT,
    iznos           NUMERIC NOT NULL,
    kreirano        TEXT    NOT NULL,
    autorizacija    TEXT
);

-- Račun ostaje sačuvan i nakon storna narudžbe (knjigovodstvena evidencija).
CREATE TABLE racuni (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    narudzba_id INTEGER NOT NULL,
    kupac       TEXT    NOT NULL,
    datoteka    TEXT    NOT NULL
);
