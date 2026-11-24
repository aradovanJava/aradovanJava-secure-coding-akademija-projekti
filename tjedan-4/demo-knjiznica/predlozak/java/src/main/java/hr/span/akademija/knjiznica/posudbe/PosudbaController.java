package hr.span.akademija.knjiznica.posudbe;

import hr.span.akademija.knjiznica.platforma.ApiException;
import hr.span.akademija.knjiznica.platforma.Baza;
import hr.span.akademija.knjiznica.platforma.PrijavljeniKorisnik;
import jakarta.servlet.http.HttpServletRequest;
import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** Posudbe: popis vlastitih posudbi, nova posudba i produljenje roka. */
@RestController
public class PosudbaController {

    private static final Logger log = LoggerFactory.getLogger(PosudbaController.class);
    private static final int TRAJANJE_POSUDBE_DANA = 21;
    // @@VULN K06
    // @@SECURE K06
    private static final int NAJVISE_DANA_PRODULJENJA = 14;
    private static final int NAJVISE_PRODULJENJA = 2;
    // @@END K06

    public record PosudbaZahtjev(Long knjigaId) {
    }

    public record ProduljenjeZahtjev(Integer dana) {
    }

    private record Posudba(long id, long korisnikId, long knjigaId, String naslov, LocalDate rok, int produzenja) {
    }

    private final Baza baza;
    private final ClanarinaServis clanarina;

    public PosudbaController(Baza baza, ClanarinaServis clanarina) {
        this.baza = baza;
        this.clanarina = clanarina;
    }

    @GetMapping("/api/posudbe")
    public List<Map<String, Object>> mojePosudbe(HttpServletRequest request) {
        PrijavljeniKorisnik korisnik = PrijavljeniKorisnik.iz(request);
        return posudbe("p.korisnik_id = ?", korisnik.id()).stream().map(PosudbaController::json).toList();
    }

    @PostMapping("/api/posudbe")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> posudi(@RequestBody PosudbaZahtjev zahtjev, HttpServletRequest request) {
        PrijavljeniKorisnik korisnik = PrijavljeniKorisnik.iz(request);
        if (zahtjev.knjigaId() == null) {
            throw ApiException.neispravno("Neispravan zahtjev.");
        }
        Integer postoji = baza.jdbc().queryForObject(
                "SELECT COUNT(*) FROM knjige WHERE id = ? AND skrivena = FALSE", Integer.class, zahtjev.knjigaId());
        if (postoji == null || postoji == 0) {
            throw ApiException.nijePronadjeno("Knjiga nije pronađena.");
        }
        // @@VULN K08
        try {
            clanarina.provjeri(korisnik.id());
        } catch (Exception e) {
            // sustav članarina zna vratiti status koji ne poznajemo
            log.debug("Provjera članarine nije uspjela ({}), posudba se nastavlja", e.getMessage());
        }
        // @@SECURE K08
        try {
            clanarina.provjeri(korisnik.id());
        } catch (ClanarinaServis.ClanarinaIstekla e) {
            throw ApiException.zabranjeno("Članarina je istekla.");
        } catch (RuntimeException e) {
            // fail-closed: svaka greška u sigurnosnoj provjeri znači odbijanje
            log.warn("SECURITY_EVENT LOAN_DENIED korisnik={} razlog=provjera_clanarine", korisnik.id());
            throw ApiException.zabranjeno("Posudba trenutačno nije moguća.");
        }
        // @@END K08
        LocalDate rok = LocalDate.now().plusDays(TRAJANJE_POSUDBE_DANA);
        long id = baza.umetni("INSERT INTO posudbe (korisnik_id, knjiga_id, rok) VALUES (?, ?, ?)",
                korisnik.id(), zahtjev.knjigaId(), rok);
        return Map.of("id", id, "knjigaId", zahtjev.knjigaId(), "rok", rok.toString());
    }

    @PostMapping("/api/posudbe/{id}/produzi")
    public Map<String, Object> produzi(@PathVariable long id, @RequestBody ProduljenjeZahtjev zahtjev,
                                       HttpServletRequest request) {
        PrijavljeniKorisnik korisnik = PrijavljeniKorisnik.iz(request);
        if (zahtjev.dana() == null) {
            throw ApiException.neispravno("Neispravan zahtjev.");
        }
        List<Posudba> nadjene = posudbe("p.id = ?", id);
        if (nadjene.isEmpty() || nadjene.get(0).korisnikId() != korisnik.id()) {
            throw ApiException.nijePronadjeno("Posudba nije pronađena.");
        }
        Posudba posudba = nadjene.get(0);
        // @@VULN K06
        // @@SECURE K06
        if (zahtjev.dana() < 1 || zahtjev.dana() > NAJVISE_DANA_PRODULJENJA) {
            throw ApiException.neispravno(
                    "Posudba se može produljiti za 1 do " + NAJVISE_DANA_PRODULJENJA + " dana.");
        }
        if (posudba.produzenja() >= NAJVISE_PRODULJENJA) {
            throw ApiException.sukob("Posudba je već produljena najveći dopušteni broj puta.");
        }
        // @@END K06
        LocalDate noviRok = posudba.rok().plusDays(zahtjev.dana());
        baza.jdbc().update("UPDATE posudbe SET rok = ?, produzenja = produzenja + 1 WHERE id = ?", noviRok, id);
        return Map.of("id", id, "rok", noviRok.toString(), "produzenja", posudba.produzenja() + 1);
    }

    private List<Posudba> posudbe(String uvjet, long parametar) {
        return baza.jdbc().query(
                "SELECT p.id, p.korisnik_id, p.knjiga_id, k.naslov, p.rok, p.produzenja FROM posudbe p "
                        + "JOIN knjige k ON k.id = p.knjiga_id WHERE " + uvjet + " ORDER BY p.id",
                (rs, i) -> new Posudba(rs.getLong("id"), rs.getLong("korisnik_id"), rs.getLong("knjiga_id"),
                        rs.getString("naslov"), rs.getObject("rok", LocalDate.class), rs.getInt("produzenja")),
                parametar);
    }

    private static Map<String, Object> json(Posudba p) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", p.id());
        m.put("knjigaId", p.knjigaId());
        m.put("naslov", p.naslov());
        m.put("rok", p.rok().toString());
        m.put("produzenja", p.produzenja());
        return m;
    }
}
