package hr.span.akademija.okviri.sigurnost;

import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

/** app.cors.allowed-origins – popis dopuštenih origina (isti ključ kao u T2). */
@ConfigurationProperties("app.cors")
public record CorsPostavke(List<String> allowedOrigins) {

    public CorsPostavke {
        allowedOrigins = allowedOrigins == null ? List.of() : List.copyOf(allowedOrigins);
        if (allowedOrigins.contains("*")) {
            throw new IllegalArgumentException("app.cors.allowed-origins ne smije sadržavati *");
        }
    }
}
