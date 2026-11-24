package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.yaml.snakeyaml.Yaml;

/** K03 – A03 Software Supply Chain Failures: SnakeYAML 1.x (CVE-2022-1471) i učitavanje s globalnim tagovima. */
@Tag("sigurnosni")
@Tag("k03")
class K03RanjivaOvisnostTest extends ApiTest {

    private static final Pattern VERZIJA_JARA = Pattern.compile("snakeyaml-(\\d+)\\.[^/\\\\]*\\.jar");

    @Test
    @DisplayName("K03: korištena verzija SnakeYAML-a mora biti 2.x ili novija")
    void snakeYamlBarem2() {
        String lokacija = Yaml.class.getProtectionDomain().getCodeSource().getLocation().toString();
        Matcher m = VERZIJA_JARA.matcher(lokacija);
        assertThat(m.find()).as("verzija iz %s", lokacija).isTrue();
        assertThat(Integer.parseInt(m.group(1))).as("glavna verzija org.yaml:snakeyaml").isGreaterThanOrEqualTo(2);
    }

    @Test
    @DisplayName("K03: YAML s globalnim tagom Java tipa mora biti odbijen (400)")
    void globalniTagJeOdbijen() {
        // Tag !!java... traži od parsera da stvori Java objekt; siguran parser takav dokument odbija.
        String katalog = "- !!java.util.HashMap {naslov: Proba, autor: Netko, godina: 2001}\n";
        Odgovor odgovor = posalji("POST", "/api/katalog/uvoz", prijava("knjiznicar"), "application/yaml", katalog);
        assertThat(odgovor.status()).isEqualTo(400);
    }
}
