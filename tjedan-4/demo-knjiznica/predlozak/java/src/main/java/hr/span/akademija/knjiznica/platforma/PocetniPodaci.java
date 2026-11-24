package hr.span.akademija.knjiznica.platforma;

import java.time.LocalDate;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

/** Početni podaci: četiri korisnika, šest knjiga i četiri posudbe. */
@Component
public class PocetniPodaci implements ApplicationRunner {

    private final Baza baza;
    private final Lozinke lozinke;

    public PocetniPodaci(Baza baza, Lozinke lozinke) {
        this.baza = baza;
        this.lozinke = lozinke;
    }

    @Override
    public void run(ApplicationArguments args) {
        korisnik("ana", "Ana123!", "CLAN", "Ana Anić", "ana.anic@primjer.hr", "Ilica 10, Zagreb",
                "091 111 1111", "AKTIVNA");
        korisnik("marko", "Marko123!", "CLAN", "Marko Marić", "marko.maric@primjer.hr", "Vukovarska 22, Zagreb",
                "092 222 2222", "ISTEKLA");
        korisnik("iva", "Iva123!", "CLAN", "Iva Ivić", "iva.ivic@primjer.hr", "Savska 5, Zagreb",
                "095 333 3333", "SUSPENDIRANA");
        korisnik("knjiznicar", "Knjiga123!", "KNJIZNICAR", "Kata Knjižić", "kata.knjizic@knjiznica.hr",
                "Trg knjiga 1, Zagreb", "01 444 4444", "AKTIVNA");

        knjiga("Proces", "Franz Kafka", 1925, false);
        knjiga("Na Drini ćuprija", "Ivo Andrić", 1945, false);
        knjiga("Povratak Filipa Latinovicza", "Miroslav Krleža", 1932, false);
        knjiga("Zlatarovo zlato", "August Šenoa", 1871, false);
        knjiga("Čudnovate zgode šegrta Hlapića", "Ivana Brlić-Mažuranić", 1913, false);
        knjiga("Interni popis za otpis", "Knjižnica", 2026, true);

        LocalDate rok = LocalDate.of(2026, 12, 10);
        posudba(1, 1, rok);
        posudba(1, 2, rok);
        posudba(1, 3, rok);
        posudba(2, 4, rok);
    }

    private void korisnik(String ime, String lozinka, String uloga, String punoIme, String email, String adresa,
                          String telefon, String clanarina) {
        baza.umetni("INSERT INTO korisnici (korisnicko_ime, lozinka_hash, uloga, ime, email, adresa, telefon, clanarina) "
                + "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ime, lozinke.hashiraj(lozinka), uloga, punoIme, email, adresa, telefon, clanarina);
    }

    private void knjiga(String naslov, String autor, int godina, boolean skrivena) {
        baza.umetni("INSERT INTO knjige (naslov, autor, godina, skrivena) VALUES (?, ?, ?, ?)",
                naslov, autor, godina, skrivena);
    }

    private void posudba(long korisnikId, long knjigaId, LocalDate rok) {
        baza.umetni("INSERT INTO posudbe (korisnik_id, knjiga_id, rok) VALUES (?, ?, ?)", korisnikId, knjigaId, rok);
    }
}
