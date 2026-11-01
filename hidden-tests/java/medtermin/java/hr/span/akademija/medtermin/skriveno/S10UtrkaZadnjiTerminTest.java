package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S10 – Utrka (CWE-362) kod rezervacije zadnjeg slobodnog mjesta (termin 7, kapacitet 1). */
@Tag("skriveno")
class S10UtrkaZadnjiTerminTest extends SkrivenoBaza {

    private static final long TERMIN = 7;
    private static final int ZAHTJEVA = 10;

    private int[] stanje() {
        Map<String, Object> red = jdbc.queryForMap("SELECT kapacitet, zauzeto FROM termini WHERE id = ?", TERMIN);
        return new int[] {((Number) red.get("kapacitet")).intValue(), ((Number) red.get("zauzeto")).intValue()};
    }

    @Test
    @DisplayName("S10: od 10 istodobnih zahtjeva za zadnje mjesto uspijeva točno jedan")
    void samoJedanDobivaZadnjeMjesto() throws Exception {
        int[] prije = stanje();
        assertThat(prije[0] - prije[1]).as("preduvjet: termin 7 ima točno jedno slobodno mjesto").isEqualTo(1);
        List<String> tokeni = new ArrayList<>();
        for (int i = 0; i < ZAHTJEVA; i++) {
            tokeni.add(prijava(noviKorisnik("utrka", "Utrka12345!"), "Utrka12345!"));
        }
        CyclicBarrier start = new CyclicBarrier(ZAHTJEVA);
        ExecutorService dretve = Executors.newFixedThreadPool(ZAHTJEVA);
        List<Integer> statusi = new ArrayList<>();
        try {
            List<Future<Integer>> rezultati = new ArrayList<>();
            for (String token : tokeni) {
                rezultati.add(dretve.submit(() -> {
                    start.await(10, TimeUnit.SECONDS);
                    return postJson("/api/rezervacije", token,
                            Map.of("terminId", TERMIN, "napomena", "Zadnji termin", "oib", "12345678903")).status();
                }));
            }
            for (Future<Integer> rezultat : rezultati) {
                statusi.add(rezultat.get(60, TimeUnit.SECONDS));
            }
        } finally {
            dretve.shutdownNow();
        }
        int[] poslije = stanje();

        assertThat(statusi.stream().filter(s -> s == 201).count())
                .as("broj uspješnih rezervacija zadnjeg mjesta (statusi: %s)", statusi).isEqualTo(1);
        assertThat(statusi.stream().filter(s -> s == 409).count()).as("ostali moraju dobiti 409").isEqualTo(ZAHTJEVA - 1);
        assertThat(poslije[1]).as("zauzeto mora biti jednako kapacitetu").isEqualTo(poslije[0]);
    }
}
