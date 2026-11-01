package hr.span.akademija.okviri;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.okviri.sigurnost.KeycloakJwtKonverter;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;

class KeycloakJwtKonverterTest {

    @Test
    void imeIzPreferredUsernameIUlogeIzRealmAccess() {
        AbstractAuthenticationToken auth = new KeycloakJwtKonverter()
                .convert(TestniKorisnici.token("dr.horvat", "LIJECNIK", "offline_access"));
        assertThat(auth.getName()).isEqualTo("dr.horvat");
        assertThat(auth.getAuthorities()).extracting(GrantedAuthority::getAuthority)
                .containsExactly("ROLE_LIJECNIK", "ROLE_offline_access");
    }

    @Test
    void bezRealmAccessNemaUloga() {
        Jwt jwt = Jwt.withTokenValue("t").header("alg", "none").subject("123").claim("x", "y").build();
        AbstractAuthenticationToken auth = new KeycloakJwtKonverter().convert(jwt);
        assertThat(auth.getAuthorities()).isEmpty();
        assertThat(auth.getName()).isEqualTo("123");
    }
}
