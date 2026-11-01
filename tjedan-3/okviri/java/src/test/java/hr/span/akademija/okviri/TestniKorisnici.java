package hr.span.akademija.okviri;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.authentication;

import hr.span.akademija.okviri.sigurnost.KeycloakJwtKonverter;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.test.web.servlet.request.RequestPostProcessor;

/**
 * "Lažni" JWT kakav izdaje Keycloak (bez Keycloaka i bez potpisa): prolazi kroz NAŠ KeycloakJwtKonverter,
 * pa testovi provjeravaju i mapiranje preferred_username / realm_access.roles.
 */
final class TestniKorisnici {

    private TestniKorisnici() {
    }

    static Jwt token(String username, String... uloge) {
        return Jwt.withTokenValue("testni-token")
                .header("alg", "none")
                .issuer("http://localhost:8180/realms/akademija")
                .subject(UUID.nameUUIDFromBytes(username.getBytes()).toString()) // Keycloak: sub je UUID
                .audience(List.of("medtermin-api"))
                .claim("preferred_username", username)
                .claim("realm_access", Map.of("roles", List.of(uloge)))
                .issuedAt(Instant.now())
                .expiresAt(Instant.now().plusSeconds(300))
                .build();
    }

    static RequestPostProcessor kao(String username, String... uloge) {
        return authentication(new KeycloakJwtKonverter().convert(token(username, uloge)));
    }
}
