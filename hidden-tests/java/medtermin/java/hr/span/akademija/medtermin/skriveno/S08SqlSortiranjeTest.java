package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S08 – SQL injection (CWE-89) u parametrima sortiranja popisa liječnika. */
@Tag("skriveno")
class S08SqlSortiranjeTest extends SkrivenoBaza {

    private int status(String upit) {
        String ana = prijava("ana", "Ana12345!");
        return get("/api/lijecnici?" + upit, ana).status();
    }

    @Test
    @DisplayName("S08: izraz s podupitom u parametru sort vraća 400")
    void podupitUSortiranju() {
        String sort = "(CASE WHEN (SELECT COUNT(*) FROM korisnici)>0 THEN prezime ELSE ime END)";

        assertThat(status("sort=" + enc(sort) + "&smjer=asc")).isEqualTo(400);
    }

    @Test
    @DisplayName("S08: točka-zarez i komentar u parametru sort vraća 400")
    void tockaZarezUSortiranju() {
        assertThat(status("sort=" + enc("prezime;--") + "&smjer=asc")).isEqualTo(400);
    }

    @Test
    @DisplayName("S08: dodatni izraz u parametru smjer vraća 400")
    void dodatniIzrazUSmjeru() {
        assertThat(status("sort=prezime&smjer=" + enc("asc,(SELECT 1)"))).isEqualTo(400);
    }
}
