package hr.span.akademija.okviri;

import static hr.span.akademija.okviri.TestniKorisnici.kao;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.options;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import hr.span.akademija.okviri.rezervacije.RezervacijaRepozitorij;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class SigurnostApiTest {

    @Autowired
    MockMvc mvc;

    @Autowired
    RezervacijaRepozitorij rezervacije;

    @BeforeEach
    void pocetniPodaci() {
        rezervacije.vratiPocetnePodatke();
    }

    @Test
    void healthJeJavan() throws Exception {
        mvc.perform(get("/api/health")).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"));
    }

    @Test
    void bezTokenaJe401UJsonFormatu() throws Exception {
        mvc.perform(get("/api/rezervacije/moje"))
                .andExpect(status().isUnauthorized())
                .andExpect(header().string("WWW-Authenticate", containsString("Bearer")))
                .andExpect(jsonPath("$.greska").value("Potrebna je prijava."));
    }

    @Test
    void mojeVracaSamoRezervacijePrijavljenogKorisnika() throws Exception {
        mvc.perform(get("/api/rezervacije/moje").with(kao("ana", "KORISNIK")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].pacijent").value("ana"))
                .andExpect(jsonPath("$[1].pacijent").value("ana"));
    }

    @Test
    void tudaRezervacijaSeNeBriseI404() throws Exception {
        mvc.perform(delete("/api/rezervacije/1").with(kao("marko", "KORISNIK")))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.greska").value("Zapis nije pronađen."));
        mvc.perform(get("/api/rezervacije/moje").with(kao("ana", "KORISNIK")))
                .andExpect(jsonPath("$[0].id").value(1));
    }

    @Test
    void nepostojecaIsto404KaoTuda() throws Exception {
        mvc.perform(delete("/api/rezervacije/999").with(kao("marko", "KORISNIK")))
                .andExpect(status().isNotFound());
    }

    @Test
    void vlasnikBriseSvoju() throws Exception {
        mvc.perform(delete("/api/rezervacije/3").with(kao("ana", "KORISNIK"))).andExpect(status().isNoContent());
        mvc.perform(get("/api/rezervacije/moje").with(kao("ana", "KORISNIK"))).andExpect(jsonPath("$", hasSize(1)));
    }

    @Test
    void adminBriseBiloKoju() throws Exception {
        mvc.perform(delete("/api/rezervacije/2").with(kao("admin", "ADMIN"))).andExpect(status().isNoContent());
    }

    @Test
    void adminskiPopisSamoZaAdmina() throws Exception {
        mvc.perform(get("/api/admin/rezervacije").with(kao("ana", "KORISNIK")))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.greska").value("Nemate ovlasti za ovu radnju."));
        mvc.perform(get("/api/admin/rezervacije").with(kao("admin", "ADMIN")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3)));
    }

    @Test
    void ugradeniJwtPostProcesorIzSpringSecurityTesta() throws Exception {
        // Standardni jwt() post-procesor; ovlasti se zadaju izravno (bez našeg konvertera).
        mvc.perform(get("/api/admin/rezervacije")
                        .with(jwt().jwt(j -> j.subject("admin")).authorities(new SimpleGrantedAuthority("ROLE_ADMIN"))))
                .andExpect(status().isOk());
    }

    @Test
    void sigurnosnaZaglavlja() throws Exception {
        mvc.perform(get("/api/health"))
                .andExpect(header().string("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"))
                .andExpect(header().string("X-Content-Type-Options", "nosniff"))
                .andExpect(header().string("X-Frame-Options", "DENY"))
                .andExpect(header().string("Referrer-Policy", "no-referrer"))
                .andExpect(header().string("Cache-Control", containsString("no-store")));
    }

    @Test
    void corsSamoZaDopusteniOrigin() throws Exception {
        mvc.perform(options("/api/rezervacije/moje")
                        .header("Origin", "http://localhost:5173")
                        .header("Access-Control-Request-Method", "GET"))
                .andExpect(status().isOk())
                .andExpect(header().string("Access-Control-Allow-Origin", "http://localhost:5173"));
        mvc.perform(options("/api/rezervacije/moje")
                        .header("Origin", "https://zlo.example")
                        .header("Access-Control-Request-Method", "GET"))
                .andExpect(status().isForbidden())
                .andExpect(header().doesNotExist("Access-Control-Allow-Origin"));
        mvc.perform(get("/api/rezervacije/moje").with(kao("ana", "KORISNIK")).header("Origin", "https://zlo.example"))
                .andExpect(header().doesNotExist("Access-Control-Allow-Origin"));
    }
}
