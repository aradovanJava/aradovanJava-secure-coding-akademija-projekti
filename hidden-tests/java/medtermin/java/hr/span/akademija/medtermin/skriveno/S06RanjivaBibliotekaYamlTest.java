package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.xml.parsers.DocumentBuilderFactory;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.yaml.snakeyaml.Yaml;

/** S06 – Ranjiva komponenta (CWE-1395/502): SnakeYAML 1.x (CVE-2022-1471). */
@Tag("skriveno")
class S06RanjivaBibliotekaYamlTest extends SkrivenoBaza {

    private static final Pattern VERZIJA_JARA = Pattern.compile("snakeyaml-(\\d+)\\.[^/\\\\]*\\.jar$");

    @Test
    @DisplayName("S06: korištena verzija SnakeYAML-a mora biti 2.x ili novija")
    void snakeYamlBarem2() throws Exception {
        Integer glavna = verzijaSKlasnePutanje();
        if (glavna == null) {
            glavna = verzijaIzPoma();
        }
        assertThat(glavna).as("glavna verzija org.yaml:snakeyaml").isGreaterThanOrEqualTo(2);
    }

    @Test
    @DisplayName("S06: YAML s globalnim tagom Java tipa mora biti odbijen (400)")
    void globalniTagJeOdbijen() {
        String ana = prijava("ana", "Ana12345!");
        String yaml = "!!java.util.HashMap {podsjetnik: true, satiPrije: 24, kanal: email}\n";

        Odgovor odgovor = posalji("POST", "/api/postavke", ana, "application/yaml", yaml);

        assertThat(odgovor.status()).as("dokument s tagom !!java... je prihvaćen").isEqualTo(400);
    }

    private static Integer verzijaSKlasnePutanje() {
        try {
            String lokacija = Yaml.class.getProtectionDomain().getCodeSource().getLocation().toString();
            Matcher m = VERZIJA_JARA.matcher(lokacija);
            return m.find() ? Integer.valueOf(m.group(1)) : null;
        } catch (RuntimeException e) {
            return null;
        }
    }

    /** Efektivna verzija iz pom.xml; ako nije navedena, verzijom upravlja Spring Boot (2.x). */
    private static int verzijaIzPoma() throws Exception {
        Path pom = Path.of("pom.xml");
        assertThat(pom).as("pom.xml u radnom direktoriju").exists();
        DocumentBuilderFactory tvornica = DocumentBuilderFactory.newInstance();
        tvornica.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        Document dokument = tvornica.newDocumentBuilder().parse(Files.newInputStream(pom));
        String verzija = null;
        NodeList ovisnosti = dokument.getElementsByTagName("dependency");
        for (int i = 0; i < ovisnosti.getLength(); i++) {
            Element ovisnost = (Element) ovisnosti.item(i);
            if ("snakeyaml".equals(dijete(ovisnost, "artifactId")) && dijete(ovisnost, "version") != null) {
                verzija = dijete(ovisnost, "version");
            }
        }
        if (verzija == null) {
            verzija = "${snakeyaml.version}";
        }
        Matcher svojstvo = Pattern.compile("\\$\\{(.+)}").matcher(verzija.trim());
        if (svojstvo.matches()) {
            NodeList svojstva = dokument.getElementsByTagName(svojstvo.group(1));
            if (svojstva.getLength() == 0) {
                return 2;
            }
            verzija = svojstva.item(0).getTextContent();
        }
        return Integer.parseInt(verzija.trim().split("[.\\-]")[0]);
    }

    private static String dijete(Element roditelj, String naziv) {
        for (Node n = roditelj.getFirstChild(); n != null; n = n.getNextSibling()) {
            if (n instanceof Element e && naziv.equals(e.getTagName())) {
                return e.getTextContent().trim();
            }
        }
        return null;
    }
}
