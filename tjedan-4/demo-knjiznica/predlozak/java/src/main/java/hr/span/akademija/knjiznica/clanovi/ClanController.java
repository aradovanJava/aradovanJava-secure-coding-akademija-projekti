package hr.span.akademija.knjiznica.clanovi;

import hr.span.akademija.knjiznica.platforma.ApiException;
import hr.span.akademija.knjiznica.platforma.Baza;
import hr.span.akademija.knjiznica.platforma.PrijavljeniKorisnik;
import jakarta.servlet.http.HttpServletRequest;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

/** Profil člana knjižnice. */
@RestController
public class ClanController {

    private final Baza baza;

    public ClanController(Baza baza) {
        this.baza = baza;
    }

    @GetMapping("/api/clanovi/{id}")
    public Map<String, Object> profil(@PathVariable long id, HttpServletRequest request) {
        PrijavljeniKorisnik korisnik = PrijavljeniKorisnik.iz(request);
        // @@VULN K01
        // @@SECURE K01
        // Član vidi samo svoj profil; knjižničar vidi sve. Tuđi profil = 404 (ne otkrivamo postoji li).
        if (id != korisnik.id() && !korisnik.jeKnjiznicar()) {
            throw ApiException.nijePronadjeno("Član nije pronađen.");
        }
        // @@END K01
        List<Map<String, Object>> profili = baza.jdbc().query(
                "SELECT id, korisnicko_ime, ime, email, adresa, telefon FROM korisnici WHERE id = ?",
                (rs, i) -> {
                    Map<String, Object> p = new LinkedHashMap<>();
                    p.put("id", rs.getLong("id"));
                    p.put("korisnickoIme", rs.getString("korisnicko_ime"));
                    p.put("ime", rs.getString("ime"));
                    p.put("email", rs.getString("email"));
                    p.put("adresa", rs.getString("adresa"));
                    p.put("telefon", rs.getString("telefon"));
                    return p;
                },
                id);
        if (profili.isEmpty()) {
            throw ApiException.nijePronadjeno("Član nije pronađen.");
        }
        return profili.get(0);
    }
}
