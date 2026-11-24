package hr.span.akademija.knjiznica.platforma;

import java.sql.PreparedStatement;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Component;

/** Pomoćne metode nad JdbcTemplateom. */
@Component
public class Baza {

    private final JdbcTemplate jdbc;

    public Baza(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public JdbcTemplate jdbc() {
        return jdbc;
    }

    /** INSERT s parametrima; vraća generirani id. */
    public long umetni(String sql, Object... parametri) {
        KeyHolder kljuc = new GeneratedKeyHolder();
        jdbc.update(veza -> {
            PreparedStatement ps = veza.prepareStatement(sql, new String[] {"ID"});
            for (int i = 0; i < parametri.length; i++) {
                ps.setObject(i + 1, parametri[i]);
            }
            return ps;
        }, kljuc);
        return kljuc.getKey().longValue();
    }
}
