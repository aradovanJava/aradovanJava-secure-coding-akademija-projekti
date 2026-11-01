package hr.span.akademija.okviri;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import hr.span.akademija.okviri.prijava.LokalniKorisnici;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class LozinkeTest {

    @Autowired
    PasswordEncoder encoder;

    @Autowired
    LokalniKorisnici korisnici;

    @Autowired
    MockMvc mvc;

    @Test
    void noviHashJeArgon2SaSolju() {
        String prvi = encoder.encode("Lozinka123!");
        String drugi = encoder.encode("Lozinka123!");
        assertThat(prvi).startsWith("{argon2}").isNotEqualTo(drugi); // sol: ista lozinka, različit hash
        assertThat(encoder.matches("Lozinka123!", prvi)).isTrue();
        assertThat(encoder.matches("Kriva", prvi)).isFalse();
        assertThat(encoder.upgradeEncoding(prvi)).isFalse();
    }

    @Test
    void stariHasheviSeProvjeravajuIOznacavajuZaNadogradnju() {
        String bcrypt = "{bcrypt}" + new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder().encode("x");
        assertThat(encoder.matches("x", bcrypt)).isTrue();
        assertThat(encoder.upgradeEncoding(bcrypt)).isTrue();
        String sha = "{sha256}78bc5813d03977dbf07326fae76c9a3e1504f4c20291cf523b6a95d148a904b9";
        assertThat(encoder.matches("Marko12345!", sha)).isTrue();
        assertThat(encoder.upgradeEncoding(sha)).isTrue();
    }

    @Test
    void prijavaMigriraStariSha256HashUArgon2() throws Exception {
        // ovaj test koristi zaseban (cache-iran) kontekst; ana i marko = 2 pokušaja od 5
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"username\":\"marko\",\"password\":\"Marko12345!\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("marko"));
        assertThat(korisnici.hash("marko")).get().asString().startsWith("{argon2}");
    }

    @Test
    void pogresnaLozinkaINepostojeciKorisnikDajuIstiOdgovor() throws Exception {
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"username\":\"ana\",\"password\":\"pogresna\"}"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.greska").value("Neispravno korisničko ime ili lozinka."));
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"username\":\"nepostoji\",\"password\":\"pogresna\"}"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.greska").value("Neispravno korisničko ime ili lozinka."));
    }
}
