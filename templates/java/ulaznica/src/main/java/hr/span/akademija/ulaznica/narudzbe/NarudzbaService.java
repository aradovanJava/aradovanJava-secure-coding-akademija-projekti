package hr.span.akademija.ulaznica.narudzbe;

import hr.span.akademija.ulaznica.platforma.ApiException;
import hr.span.akademija.ulaznica.platforma.JdbcPomoc;
import hr.span.akademija.ulaznica.platforma.PrijavljeniKorisnik;
import hr.span.akademija.ulaznica.racuni.RacunService;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class NarudzbaService {

    private static final Logger log = LoggerFactory.getLogger(NarudzbaService.class);
    private static final Pattern OIB = Pattern.compile("\\d{11}");

    public record NovaNarudzba(Long dogadjajId, Integer kolicina, String imeNaUlaznici, String oib) {
    }

    public record Narudzba(long id, long dogadjajId, String dogadjaj, String mjesto, LocalDateTime datum,
                           String kupac, int kolicina, String imeNaUlaznici, BigDecimal iznos,
                           LocalDateTime kreirano) {
    }

    private static final String SELECT = "SELECT n.id, n.dogadjaj_id, d.naziv, d.mjesto, d.datum, n.kupac, "
            + "n.kolicina, n.ime_na_ulaznici, n.iznos, n.kreirano FROM narudzbe n "
            + "JOIN dogadjaji d ON d.id = n.dogadjaj_id";

    private static final RowMapper<Narudzba> MAPPER = (rs, i) -> new Narudzba(
            rs.getLong("id"), rs.getLong("dogadjaj_id"), rs.getString("naziv"), rs.getString("mjesto"),
            rs.getObject("datum", LocalDateTime.class), rs.getString("kupac"), rs.getInt("kolicina"),
            rs.getString("ime_na_ulaznici"), rs.getBigDecimal("iznos"), rs.getObject("kreirano", LocalDateTime.class));

    private final JdbcTemplate jdbc;
    private final PlatniSustavKlijent placanje;
    private final RacunService racuni;

    public NarudzbaService(JdbcTemplate jdbc, PlatniSustavKlijent placanje, RacunService racuni) {
        this.jdbc = jdbc;
        this.placanje = placanje;
        this.racuni = racuni;
    }

    public Optional<Narudzba> pronadi(long id) {
        return jdbc.query(SELECT + " WHERE n.id = ?", MAPPER, id).stream().findFirst();
    }

    public List<Narudzba> narudzbeKupca(String username) {
        return jdbc.query(SELECT + " WHERE n.kupac = ? ORDER BY d.datum, n.id", MAPPER, username);
    }

    public long kreiraj(NovaNarudzba zahtjev, PrijavljeniKorisnik korisnik) {
        if (zahtjev == null || zahtjev.dogadjajId() == null) {
            throw ApiException.neispravno("Događaj je obavezan.");
        }
        int kolicina = zahtjev.kolicina() == null ? 1 : zahtjev.kolicina();
        if (kolicina < 1 || kolicina > 4) {
            throw ApiException.neispravno("Količina mora biti između 1 i 4.");
        }
        if (zahtjev.imeNaUlaznici() == null || zahtjev.imeNaUlaznici().isBlank()
                || zahtjev.imeNaUlaznici().length() > 200) {
            throw ApiException.neispravno("Ime na ulaznici je obavezno (najviše 200 znakova).");
        }
        if (zahtjev.oib() == null || !OIB.matcher(zahtjev.oib()).matches()) {
            throw ApiException.neispravno("OIB mora imati 11 znamenki.");
        }
        long dogadjajId = zahtjev.dogadjajId();
        List<Map<String, Object>> dogadjaji = jdbc.queryForList(
                "SELECT naziv, cijena FROM dogadjaji WHERE id = ?", dogadjajId);
        if (dogadjaji.isEmpty()) {
            throw ApiException.nijePronadeno("Događaj nije pronađen.");
        }
        String naziv = (String) dogadjaji.get(0).get("naziv");
        BigDecimal iznos = ((BigDecimal) dogadjaji.get(0).get("cijena")).multiply(BigDecimal.valueOf(kolicina));
        // @@VULN S12
        log.info("Nova narudžba: {} (kupac {})", zahtjev, korisnik.username());
        // @@SECURE S12
        log.info("Nova narudžba: događaj {}, količina {}, kupac {}, OIB {}", dogadjajId, kolicina,
                korisnik.username(), maskirajOib(zahtjev.oib()));
        // @@END S12
        // @@VULN S10
        Map<String, Object> stanje = jdbc.queryForMap("SELECT kapacitet, prodano FROM dogadjaji WHERE id = ?",
                dogadjajId);
        int kapacitet = ((Number) stanje.get("kapacitet")).intValue();
        int prodano = ((Number) stanje.get("prodano")).intValue();
        if (prodano + kolicina > kapacitet) {
            throw new ApiException(HttpStatus.CONFLICT, "Nema slobodnih mjesta.");
        }
        String autorizacija = placanje.autoriziraj(korisnik.username(), iznos);
        jdbc.update("UPDATE dogadjaji SET prodano = prodano + ? WHERE id = ?", kolicina, dogadjajId);
        return spremi(zahtjev, kolicina, iznos, naziv, korisnik, autorizacija);
        // @@SECURE S10
        int azurirano = jdbc.update(
                "UPDATE dogadjaji SET prodano = prodano + ? WHERE id = ? AND prodano + ? <= kapacitet",
                kolicina, dogadjajId, kolicina);
        if (azurirano == 0) {
            throw new ApiException(HttpStatus.CONFLICT, "Nema slobodnih mjesta.");
        }
        try {
            String autorizacija = placanje.autoriziraj(korisnik.username(), iznos);
            return spremi(zahtjev, kolicina, iznos, naziv, korisnik, autorizacija);
        } catch (RuntimeException e) {
            jdbc.update("UPDATE dogadjaji SET prodano = prodano - ? WHERE id = ?", kolicina, dogadjajId);
            throw e;
        }
        // @@END S10
    }

    /** Storno narudžbe; račun ostaje sačuvan. */
    @Transactional
    public void storniraj(long id, PrijavljeniKorisnik korisnik) {
        // @@VULN S01
        Narudzba narudzba = pronadi(id)
                .orElseThrow(() -> ApiException.nijePronadeno("Narudžba nije pronađena."));
        // @@SECURE S01
        Narudzba narudzba = pronadi(id)
                .filter(n -> korisnik.isAdmin() || n.kupac().equals(korisnik.username()))
                .orElseThrow(() -> ApiException.nijePronadeno("Narudžba nije pronađena."));
        // @@END S01
        jdbc.update("DELETE FROM narudzbe WHERE id = ?", narudzba.id());
        jdbc.update("UPDATE dogadjaji SET prodano = prodano - ? WHERE id = ? AND prodano >= ?",
                narudzba.kolicina(), narudzba.dogadjajId(), narudzba.kolicina());
        log.info("Narudžba {} je stornirana (korisnik {})", id, korisnik.username());
    }

    private long spremi(NovaNarudzba zahtjev, int kolicina, BigDecimal iznos, String dogadjaj,
                        PrijavljeniKorisnik korisnik, String autorizacija) {
        long id = JdbcPomoc.umetni(jdbc,
                "INSERT INTO narudzbe (dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, iznos, kreirano, "
                        + "autorizacija) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                zahtjev.dogadjajId(), korisnik.username(), kolicina, zahtjev.imeNaUlaznici(), zahtjev.oib(), iznos,
                LocalDateTime.now(), autorizacija);
        racuni.izdaj(id, korisnik.username(), dogadjaj, kolicina, iznos, autorizacija);
        return id;
    }
    // @@VULN S12
    // @@SECURE S12

    private static String maskirajOib(String oib) {
        if (oib == null || oib.length() < 4) {
            return "***";
        }
        return "*".repeat(oib.length() - 4) + oib.substring(oib.length() - 4);
    }
    // @@END S12
}
