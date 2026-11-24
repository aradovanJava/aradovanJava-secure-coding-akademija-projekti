package hr.span.akademija.knjiznica.platforma;

import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** Prijava i registracija članova. */
@RestController
public class PrijavaController {

    private static final Logger log = LoggerFactory.getLogger(PrijavaController.class);
    private static final Pattern KORISNICKO_IME = Pattern.compile("[a-z0-9._-]{3,40}");

    public record PrijavaZahtjev(String korisnickoIme, String lozinka) {
    }

    public record RegistracijaZahtjev(String korisnickoIme, String lozinka, String ime, String email) {
    }

    private record Racun(long id, String korisnickoIme, String uloga, String lozinkaHash) {
    }

    private final Baza baza;
    private final Lozinke lozinke;
    private final Tokeni tokeni;

    public PrijavaController(Baza baza, Lozinke lozinke, Tokeni tokeni) {
        this.baza = baza;
        this.lozinke = lozinke;
        this.tokeni = tokeni;
    }

    @PostMapping("/api/prijava")
    public Map<String, Object> prijava(@RequestBody PrijavaZahtjev zahtjev, HttpServletRequest request) {
        if (zahtjev.korisnickoIme() == null || zahtjev.lozinka() == null) {
            throw ApiException.neispravno("Neispravan zahtjev.");
        }
        String ip = request.getRemoteAddr();
        List<Racun> racuni = baza.jdbc().query(
                "SELECT id, korisnicko_ime, uloga, lozinka_hash FROM korisnici WHERE korisnicko_ime = ?",
                (rs, i) -> new Racun(rs.getLong("id"), rs.getString("korisnicko_ime"), rs.getString("uloga"),
                        rs.getString("lozinka_hash")),
                zahtjev.korisnickoIme());
        Racun racun = racuni.isEmpty() ? null : racuni.get(0);
        // @@VULN K07
        log.info("Prijava korisnika {} (lozinka: {}) s adrese {}", zahtjev.korisnickoIme(), zahtjev.lozinka(), ip);
        if (racun == null || !lozinke.provjeri(zahtjev.lozinka(), racun.lozinkaHash())) {
            throw ApiException.neispravnaPrijava();
        }
        // @@SECURE K07
        if (racun == null || !lozinke.provjeri(zahtjev.lozinka(), racun.lozinkaHash())) {
            log.warn("SECURITY_EVENT LOGIN_FAILED korisnik={} ip={}", ocisti(zahtjev.korisnickoIme()), ip);
            throw ApiException.neispravnaPrijava();
        }
        log.info("SECURITY_EVENT LOGIN_SUCCESS korisnik={} ip={}", ocisti(racun.korisnickoIme()), ip);
        // @@END K07
        return Map.of("token", tokeni.izdaj(racun.id()), "korisnickoIme", racun.korisnickoIme(),
                "uloga", racun.uloga());
    }
    // @@VULN K07
    // @@SECURE K07

    /** Neutralizira znakove za novi red da korisnički unos ne može krivotvoriti zapis u dnevniku. */
    private static String ocisti(String tekst) {
        return tekst.replace('\r', '_').replace('\n', '_');
    }
    // @@END K07

    @PostMapping("/api/registracija")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> registracija(@RequestBody RegistracijaZahtjev zahtjev) {
        if (zahtjev.korisnickoIme() == null || !KORISNICKO_IME.matcher(zahtjev.korisnickoIme()).matches()
                || zahtjev.lozinka() == null || zahtjev.lozinka().length() < 8
                || zahtjev.ime() == null || zahtjev.ime().isBlank()
                || zahtjev.email() == null || !zahtjev.email().contains("@")) {
            throw ApiException.neispravno("Neispravni podaci za registraciju.");
        }
        Integer postoji = baza.jdbc().queryForObject(
                "SELECT COUNT(*) FROM korisnici WHERE korisnicko_ime = ?", Integer.class, zahtjev.korisnickoIme());
        if (postoji != null && postoji > 0) {
            throw ApiException.sukob("Korisničko ime je zauzeto.");
        }
        long id = baza.umetni(
                "INSERT INTO korisnici (korisnicko_ime, lozinka_hash, uloga, ime, email) VALUES (?, ?, 'CLAN', ?, ?)",
                zahtjev.korisnickoIme(), lozinke.hashiraj(zahtjev.lozinka()), zahtjev.ime().strip(),
                zahtjev.email().strip());
        return Map.of("id", id);
    }
}
