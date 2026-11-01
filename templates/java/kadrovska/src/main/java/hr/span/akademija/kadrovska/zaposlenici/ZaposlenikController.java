package hr.span.akademija.kadrovska.zaposlenici;

import hr.span.akademija.kadrovska.platforma.PrijavljeniKorisnik;
import java.util.List;
// @@VULN S08
// @@SECURE S08
import hr.span.akademija.kadrovska.platforma.ApiException;
import java.util.Locale;
import java.util.Map;
// @@END S08
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Imenik zaposlenika. */
@RestController
@RequestMapping("/api/zaposlenici")
public class ZaposlenikController {

    public record Zaposlenik(long id, String ime, String prezime, String odjel, String email) {
    }

    private static final RowMapper<Zaposlenik> MAPPER = (rs, i) -> new Zaposlenik(rs.getLong("id"),
            rs.getString("ime"), rs.getString("prezime"), rs.getString("odjel"), rs.getString("email"));

    // @@VULN S08
    // @@SECURE S08
    private static final Map<String, String> STUPCI = Map.of(
            "ime", "ime",
            "prezime", "prezime",
            "odjel", "odjel");
    // @@END S08

    private final JdbcTemplate jdbc;

    public ZaposlenikController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    /** Popis zaposlenika, npr. {@code GET /api/zaposlenici?sort=prezime&smjer=asc}. */
    @GetMapping
    public List<Zaposlenik> popis(@RequestParam(defaultValue = "prezime") String sort,
                                  @RequestParam(defaultValue = "asc") String smjer,
                                  PrijavljeniKorisnik korisnik) {
        // @@VULN S08
        String sql = "SELECT id, ime, prezime, odjel, email FROM zaposlenici ORDER BY " + sort + " " + smjer;
        // @@SECURE S08
        String stupac = STUPCI.get(sort);
        String redoslijed = switch (smjer.toLowerCase(Locale.ROOT)) {
            case "asc" -> "ASC";
            case "desc" -> "DESC";
            default -> null;
        };
        if (stupac == null || redoslijed == null) {
            throw ApiException.neispravno("Neispravan parametar sortiranja.");
        }
        String sql = "SELECT id, ime, prezime, odjel, email FROM zaposlenici ORDER BY "
                + stupac + " " + redoslijed + ", id";
        // @@END S08
        return jdbc.query(sql, MAPPER);
    }
}
