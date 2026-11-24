package hr.span.akademija.knjiznica.posudbe;

import hr.span.akademija.knjiznica.platforma.Baza;
import java.util.List;
import org.springframework.stereotype.Service;

/** Provjera članarine prije posudbe. */
@Service
public class ClanarinaServis {

    /** Članarina je istekla. */
    public static class ClanarinaIstekla extends RuntimeException {
        public ClanarinaIstekla(String poruka) {
            super(poruka);
        }
    }

    private final Baza baza;

    public ClanarinaServis(Baza baza) {
        this.baza = baza;
    }

    public void provjeri(long korisnikId) {
        List<String> statusi = baza.jdbc().queryForList(
                "SELECT clanarina FROM korisnici WHERE id = ?", String.class, korisnikId);
        String status = statusi.isEmpty() ? null : statusi.get(0);
        if ("AKTIVNA".equals(status)) {
            return;
        }
        if ("ISTEKLA".equals(status)) {
            throw new ClanarinaIstekla("Članarina je istekla.");
        }
        throw new IllegalStateException("Nepoznat status članarine: " + status);
    }
}
