package hr.span.akademija.okviri.sigurnost;

import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.ConsumptionProbe;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * Ograničavanje broja pokušaja prijave (Bucket4j, token bucket): N pokušaja u minuti po IP adresi,
 * zatim 429 Too Many Requests + Retry-After. Usporava pogađanje lozinki (brute force, credential stuffing).
 * Kante su u memoriji jedne instance; za više instanci koristite bucket4j-redis / JCache ili API gateway.
 */
public class OgranicenjePrijave extends OncePerRequestFilter {

    private static final String PUTANJA = "/api/auth/login";
    private static final int NAJVISE_KANTI = 10_000;

    private final Map<String, Bucket> kante = new ConcurrentHashMap<>();
    private final int pokusajaUMinuti;

    public OgranicenjePrijave(int pokusajaUMinuti) {
        this.pokusajaUMinuti = pokusajaUMinuti;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !("POST".equals(request.getMethod())
                && (request.getContextPath() + PUTANJA).equals(request.getRequestURI()));
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        if (kante.size() > NAJVISE_KANTI) {
            kante.clear(); // grubo ograničenje memorije (napadač s mnogo IP adresa)
        }
        // Iza reverse proxyja: server.forward-headers-strategy=native, inače su svi klijenti "isti IP".
        Bucket kanta = kante.computeIfAbsent(request.getRemoteAddr(), ip -> novaKanta());
        ConsumptionProbe proba = kanta.tryConsumeAndReturnRemaining(1);
        if (proba.isConsumed()) {
            chain.doFilter(request, response);
            return;
        }
        long sekundi = Math.max(1, TimeUnit.NANOSECONDS.toSeconds(proba.getNanosToWaitForRefill()));
        response.setHeader("Retry-After", String.valueOf(sekundi));
        JsonGreske.posalji(response, 429, "Previše pokušaja prijave. Pokušajte ponovno kasnije.");
    }

    private Bucket novaKanta() {
        return Bucket.builder()
                .addLimit(Bandwidth.builder()
                        .capacity(pokusajaUMinuti)
                        .refillIntervally(pokusajaUMinuti, Duration.ofMinutes(1))
                        .build())
                .build();
    }
}
