package hr.span.akademija.knjiznica.knjige;

import hr.span.akademija.knjiznica.platforma.ApiException;
import hr.span.akademija.knjiznica.platforma.Baza;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Pretraga kataloga i podaci o knjizi (javno, bez prijave). */
@RestController
public class KnjigaController {

    private final Baza baza;

    public KnjigaController(Baza baza) {
        this.baza = baza;
    }

    @GetMapping("/api/knjige")
    public List<Map<String, Object>> pretrazi(@RequestParam(defaultValue = "") String trazi) {
        // @@VULN K02
        String sql = "SELECT id, naslov, autor, godina FROM knjige "
                + "WHERE skrivena = FALSE AND naslov LIKE '%" + trazi + "%' ORDER BY naslov";
        return baza.jdbc().query(sql, (rs, i) -> knjiga(rs));
        // @@SECURE K02
        if (trazi.length() > 100) {
            throw ApiException.neispravno("Upit je predugačak.");
        }
        // parametrizirani upit; znakovi %, _ i \ u upitu traže se doslovno
        String uzorak = "%" + trazi.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%";
        return baza.jdbc().query(
                "SELECT id, naslov, autor, godina FROM knjige "
                        + "WHERE skrivena = FALSE AND naslov LIKE ? ESCAPE '\\' ORDER BY naslov",
                (rs, i) -> knjiga(rs), uzorak);
        // @@END K02
    }

    @GetMapping("/api/knjige/{id}")
    public Map<String, Object> dohvati(@PathVariable long id) {
        // @@VULN K05
        return baza.jdbc().queryForObject(
                "SELECT id, naslov, autor, godina FROM knjige WHERE id = ? AND skrivena = FALSE",
                (rs, i) -> knjiga(rs), id);
        // @@SECURE K05
        List<Map<String, Object>> knjige = baza.jdbc().query(
                "SELECT id, naslov, autor, godina FROM knjige WHERE id = ? AND skrivena = FALSE",
                (rs, i) -> knjiga(rs), id);
        if (knjige.isEmpty()) {
            throw ApiException.nijePronadjeno("Knjiga nije pronađena.");
        }
        return knjige.get(0);
        // @@END K05
    }

    private static Map<String, Object> knjiga(ResultSet rs) throws SQLException {
        Map<String, Object> k = new LinkedHashMap<>();
        k.put("id", rs.getLong("id"));
        k.put("naslov", rs.getString("naslov"));
        k.put("autor", rs.getString("autor"));
        k.put("godina", rs.getInt("godina"));
        return k;
    }
}
