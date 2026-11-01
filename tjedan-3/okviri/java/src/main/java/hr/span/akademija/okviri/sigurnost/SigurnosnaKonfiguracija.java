package hr.span.akademija.okviri.sigurnost;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.argon2.Argon2PasswordEncoder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.DelegatingPasswordEncoder;
import org.springframework.security.crypto.password.MessageDigestPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.server.resource.web.authentication.BearerTokenAuthenticationFilter;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.header.writers.ReferrerPolicyHeaderWriter.ReferrerPolicy;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

/**
 * Sva sigurnosna pravila na jednom mjestu – umjesto ručnih provjera razbacanih po kontrolerima (T2).
 */
@Configuration
@EnableMethodSecurity // uključuje @PreAuthorize / @PostAuthorize
public class SigurnosnaKonfiguracija {

    @Bean
    SecurityFilterChain api(HttpSecurity http, PrijavaPostavke prijava) throws Exception {
        JsonGreske greske = new JsonGreske();
        http
                // REST API s Bearer tokenom u zaglavlju (ne kolačić) -> CSRF zaštita nije potrebna.
                .csrf(csrf -> csrf.disable())
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .cors(Customizer.withDefaults()) // koristi bean corsConfigurationSource (dolje)
                // Zadano ZABRANJENO: sve što nije izričito dopušteno traži prijavu.
                .authorizeHttpRequests(a -> a
                        .requestMatchers(HttpMethod.GET, "/api/health").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/auth/login").permitAll()
                        .requestMatchers("/api/admin/**").hasRole("ADMIN")
                        .anyRequest().authenticated())
                // JWT od Keycloaka: potpis, rok valjanosti, iss i aud provjerava okvir.
                .oauth2ResourceServer(o -> o
                        .jwt(jwt -> jwt.jwtAuthenticationConverter(new KeycloakJwtKonverter()))
                        .authenticationEntryPoint(greske)
                        .accessDeniedHandler(greske))
                .exceptionHandling(e -> e.authenticationEntryPoint(greske).accessDeniedHandler(greske))
                // Sigurnosna zaglavlja: X-Content-Type-Options, Cache-Control i X-Frame-Options su zadani; dodajemo CSP i Referrer-Policy.
                .headers(h -> h
                        .contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'none'; frame-ancestors 'none'"))
                        .frameOptions(f -> f.deny())
                        .referrerPolicy(r -> r.policy(ReferrerPolicy.NO_REFERRER)))
                // Ograničenje broja pokušaja prijave (Bucket4j) prije autentikacije.
                .addFilterBefore(new OgranicenjePrijave(prijava.pokusajaUMinuti()), BearerTokenAuthenticationFilter.class);
        return http.build();
    }

    /** CORS iz konfiguracije (app.cors.allowed-origins) – samo točno navedeni origini, nikad refleksija. */
    @Bean
    CorsConfigurationSource corsConfigurationSource(CorsPostavke postavke) {
        CorsConfiguration cors = new CorsConfiguration();
        cors.setAllowedOrigins(postavke.allowedOrigins());
        cors.setAllowedMethods(List.of("GET", "POST", "DELETE"));
        cors.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        cors.setAllowCredentials(false); // token je u zaglavlju Authorization, kolačići nisu potrebni
        cors.setMaxAge(Duration.ofHours(1));
        UrlBasedCorsConfigurationSource izvor = new UrlBasedCorsConfigurationSource();
        izvor.registerCorsConfiguration("/api/**", cors);
        return izvor;
    }

    /**
     * Hashevi oblika {id}hash: novi se uvijek rade Argon2id algoritmom, stari (bcrypt, SHA-256 iz T2)
     * se još mogu provjeriti, a upgradeEncoding() javlja da ih treba zamijeniti nakon uspješne prijave.
     */
    @Bean
    @SuppressWarnings("deprecation")
    PasswordEncoder passwordEncoder() {
        Map<String, PasswordEncoder> enkoderi = new HashMap<>();
        enkoderi.put("argon2", Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8());
        enkoderi.put("bcrypt", new BCryptPasswordEncoder());
        // Zastarjelo NAMJERNO: samo za PROVJERU starih SHA-256 hasheva bez soli (T2) dok se ne migriraju.
        enkoderi.put("sha256", new MessageDigestPasswordEncoder("SHA-256"));
        return new DelegatingPasswordEncoder("argon2", enkoderi);
    }
}
