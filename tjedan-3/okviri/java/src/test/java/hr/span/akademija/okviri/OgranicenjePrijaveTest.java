package hr.span.akademija.okviri;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

/** Vlastiti kontekst (drukčije postavke) = svježe kante, neovisno o drugim testovima. */
@SpringBootTest(properties = "app.prijava.pokusaja-u-minuti=3")
@AutoConfigureMockMvc
class OgranicenjePrijaveTest {

    @Autowired
    MockMvc mvc;

    private static MockHttpServletRequestBuilder pokusaj() {
        return post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                .content("{\"username\":\"ana\",\"password\":\"pogadam\"}");
    }

    @Test
    void nakonTriPokusajaSlijedi429() throws Exception {
        for (int i = 0; i < 3; i++) {
            mvc.perform(pokusaj()).andExpect(status().isUnauthorized());
        }
        mvc.perform(pokusaj())
                .andExpect(status().isTooManyRequests())
                .andExpect(header().exists("Retry-After"))
                .andExpect(jsonPath("$.greska").value("Previše pokušaja prijave. Pokušajte ponovno kasnije."));
    }
}
