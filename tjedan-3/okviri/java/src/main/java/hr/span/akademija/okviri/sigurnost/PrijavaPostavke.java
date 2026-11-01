package hr.span.akademija.okviri.sigurnost;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

/** app.prijava.pokusaja-u-minuti – koliko pokušaja prijave po IP adresi u minuti. */
@ConfigurationProperties("app.prijava")
public record PrijavaPostavke(@DefaultValue("5") int pokusajaUMinuti) {
}
