CREATE TABLE korisnici (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    korisnicko_ime VARCHAR(40)  NOT NULL UNIQUE,
    lozinka_hash   VARCHAR(200) NOT NULL,
    uloga          VARCHAR(20)  NOT NULL,
    ime            VARCHAR(100) NOT NULL,
    email          VARCHAR(200) NOT NULL,
    adresa         VARCHAR(200) DEFAULT '' NOT NULL,
    telefon        VARCHAR(40)  DEFAULT '' NOT NULL,
    clanarina      VARCHAR(20)  DEFAULT 'AKTIVNA' NOT NULL
);

CREATE TABLE knjige (
    id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    naslov   VARCHAR(200) NOT NULL,
    autor    VARCHAR(200) NOT NULL,
    godina   INT          NOT NULL,
    skrivena BOOLEAN      DEFAULT FALSE NOT NULL
);

CREATE TABLE posudbe (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    korisnik_id BIGINT NOT NULL REFERENCES korisnici (id),
    knjiga_id   BIGINT NOT NULL REFERENCES knjige (id),
    rok         DATE   NOT NULL,
    produzenja  INT    DEFAULT 0 NOT NULL
);
