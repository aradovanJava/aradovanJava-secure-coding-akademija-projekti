package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** K01 – A01 Broken Access Control: pristup tuđem profilu promjenom ID-a (IDOR, CWE-639). */
@Tag("sigurnosni")
@Tag("k01")
class K01TudjiProfilTest extends ApiTest {

    @Test
    @DisplayName("K01: član ne vidi tuđi profil (404, bez tuđih podataka)")
    void clanNeVidiTudjiProfil() {
        // Ana (id 1) traži Markov profil (id 2).
        Odgovor odgovor = get("/api/clanovi/2", prijava("ana"));
        assertThat(odgovor.status()).isEqualTo(404);
        assertThat(odgovor.tijelo()).doesNotContainIgnoringCase("marko").doesNotContain("Vukovarska");
    }

    @Test
    @DisplayName("K01: odgovor ne otkriva postoji li član")
    void odgovorNeOtkrivaPostojanje() {
        Odgovor tudji = get("/api/clanovi/2", prijava("ana"));
        Odgovor nepostojeci = get("/api/clanovi/999", prijava("ana"));
        assertThat(tudji.status()).isEqualTo(nepostojeci.status());
        assertThat(tudji.tijelo()).isEqualTo(nepostojeci.tijelo());
    }
}
