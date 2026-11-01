package hr.span.akademija.okviri.sigurnost;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

/**
 * Keycloak JWT -> Authentication: ime korisnika iz preferred_username, uloge iz realm_access.roles
 * (KORISNIK, LIJECNIK, ADMIN) kao ROLE_* ovlasti za hasRole(...).
 */
public class KeycloakJwtKonverter implements Converter<Jwt, AbstractAuthenticationToken> {

    @Override
    public AbstractAuthenticationToken convert(Jwt jwt) {
        String ime = jwt.getClaimAsString("preferred_username");
        return new JwtAuthenticationToken(jwt, uloge(jwt), ime != null ? ime : jwt.getSubject());
    }

    static Collection<GrantedAuthority> uloge(Jwt jwt) {
        Map<String, Object> realmAccess = jwt.getClaimAsMap("realm_access");
        if (realmAccess == null || !(realmAccess.get("roles") instanceof Collection<?> uloge)) {
            return List.of();
        }
        return uloge.stream()
                .map(u -> (GrantedAuthority) new SimpleGrantedAuthority("ROLE_" + u))
                .toList();
    }
}
