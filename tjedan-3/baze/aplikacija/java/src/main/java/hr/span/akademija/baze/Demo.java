package hr.span.akademija.baze;

import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Demo „Aplikacija i baza” (Java, JDBC): što aplikacijski račun smije u bazi.
 *
 * <p>Program se spaja na SQL Server iz laboratorija ONAKO KAKO SE SPAJA APLIKACIJA: prijavom
 * {@code <domena>_app} (ne sa!), šifriranom vezom, lozinkom iz varijable okruženja (nikad iz koda ni iz
 * repozitorija), isključivo parametriziranim upitima, i na početku „zahtjeva” postavlja SESSION_CONTEXT s
 * prijavljenim korisnikom (za Row-Level Security). Zatim ispisuje što taj račun stvarno smije. Pokrenite ga
 * PRIJE zadataka (zatečeno stanje) i POSLIJE zadataka Z2–Z4: upozorenja [!] moraju nestati.
 *
 * <p>Pokretanje (README.md, odjeljak „Demo: aplikacija i baza”):
 * {@code docker compose --profile aplikacija run --rm aplikacija-java} ili lokalno {@code ./mvnw -q compile exec:java}.
 * Postavke (varijable okruženja): DOMENA, SQL_HOST, SQL_PORT, APP_LOZINKA, PODRSKA_LOZINKA.
 */
public final class Demo {

    /** Baza, glavna tablica i stupac vlasnika za jednu domenu. */
    private record Domena(String baza, String glavna, String vlasnik) { }

    // Nazivi tablica i stupaca NE MOGU biti parametri upita, zato dolaze isključivo iz ovog popisa dopuštenih
    // vrijednosti – nikad iz korisničkog unosa (usporedi S08 iz T2).
    private static final Map<String, Domena> DOMENE = Map.of(
            "medtermin", new Domena("MedTermin", "rezervacije", "pacijent"),
            "ulaznica", new Domena("Ulaznica", "narudzbe", "kupac"),
            "kadrovska", new Domena("Kadrovska", "zahtjevi", "zaposlenik"));
    private static final String ZLONAMJERNI_UNOS = "x' OR 1=1 --";

    private static final PrintStream IZLAZ = new PrintStream(System.out, true, StandardCharsets.UTF_8);
    private static final List<String[]> REZULTATI = new ArrayList<>(); // strojno čitljivi sažetak (DEMO|ključ|vrijednost)
    private static int upozorenja;

    private static String domena;
    private static Domena d;
    private static String host;
    private static String port;
    private static String app;
    private static String appLozinka;
    private static boolean zatecenaLozinka;
    private static String podrskaLozinka;

    private Demo() { }

    public static void main(String[] args) {
        int kod = pokreni();
        if (kod != 0) {
            System.exit(kod);
        }
    }

    private static String okolina(String ime, String zadano) {
        String v = System.getenv(ime);
        return v == null || v.isBlank() ? zadano : v;
    }

    /**
     * Nova veza. encrypt=true: promet je šifriran (TLS). trustServerCertificate=true smije stajati SAMO u
     * laboratoriju (samopotpisani certifikat poslužitelja); u produkciji certifikat kojem klijent vjeruje.
     */
    private static Connection spoji(String prijava, String lozinka) throws SQLException {
        String url = "jdbc:sqlserver://" + host + ":" + port + ";databaseName=" + d.baza()
                + ";encrypt=true;trustServerCertificate=true;loginTimeout=15";
        Connection veza = DriverManager.getConnection(url, prijava, lozinka); // lozinka nije dio URL-a
        veza.setAutoCommit(false); // pokušaje poništavamo (ROLLBACK)
        return veza;
    }

    /** Veza aplikacije za jedan „zahtjev”: nakon prijave korisnika aplikacija bazi kaže tko je on. */
    private static Connection kaoKorisnik(String korisnik) throws SQLException {
        Connection veza = spoji(app, appLozinka);
        if (korisnik != null) {
            // @read_only = 1: kasniji kod (pa ni SQL injection) u istoj sesiji više ne može promijeniti identitet.
            try (PreparedStatement ps = veza.prepareStatement(
                    "EXEC sp_set_session_context @key = N'korisnik', @value = ?, @read_only = 1")) {
                ps.setString(1, korisnik);
                ps.execute();
            }
        }
        return veza;
    }

    /** Prvi stupac prvog retka. Parametri se šalju odvojeno od teksta upita (oznake ?). */
    private static long vrijednost(Connection veza, String upit, String... parametri) throws SQLException {
        try (PreparedStatement ps = veza.prepareStatement(upit)) {
            for (int i = 0; i < parametri.length; i++) {
                ps.setString(i + 1, parametri[i]);
            }
            try (ResultSet rs = ps.executeQuery()) {
                rs.next();
                return rs.getLong(1);
            }
        }
    }

    /** true ako baza dopusti naredbu; pokušaj se uvijek poništava (i CREATE TABLE je dio transakcije). */
    private static boolean pokusaj(Connection veza, String naredba) throws SQLException {
        try (Statement st = veza.createStatement()) {
            st.execute(naredba);
            return true;
        } catch (SQLException odbijeno) {
            return false;
        } finally {
            veza.rollback();
        }
    }

    private static String redaka(long n) {
        if (n % 10 == 1 && n % 100 != 11) {
            return n + " redak";
        }
        if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)) {
            return n + " retka";
        }
        return n + " redaka";
    }

    private static void ispis(String opis, String stanje, String upozorenje, String napomena) {
        StringBuilder oznaka = new StringBuilder(opis).append(' ');
        while (oznaka.length() < 36) {
            oznaka.append('.');
        }
        String dodatak = "";
        if (upozorenje != null && !upozorenje.isEmpty()) {
            upozorenja++;
            dodatak = "  [!] " + upozorenje;
        } else if (napomena != null && !napomena.isEmpty()) {
            dodatak = "  (" + napomena + ")";
        }
        IZLAZ.println("   " + oznaka + " " + stanje + dodatak);
    }

    private static void ispis(String opis, String stanje, String upozorenje) {
        ispis(opis, stanje, upozorenje, "");
    }

    private static String daNe(boolean uvjet) {
        return uvjet ? "DA" : "NE";
    }

    private static void rezultat(String kljuc, String stanje) {
        REZULTATI.add(new String[] {kljuc, stanje});
    }

    private static String prviRedak(SQLException greska, int najvise) {
        String poruka = String.valueOf(greska.getMessage()).lines().findFirst().orElse("");
        return poruka.length() > najvise ? poruka.substring(0, najvise) : poruka;
    }

    private static int pokreni() {
        domena = okolina("DOMENA", "medtermin").trim().toLowerCase(Locale.ROOT);
        d = DOMENE.get(domena);
        if (d == null) {
            IZLAZ.println("DOMENA mora biti medtermin, ulaznica ili kadrovska (sada: '" + domena + "').");
            return 2;
        }
        host = okolina("SQL_HOST", "localhost");
        port = okolina("SQL_PORT", "1433");
        app = domena + "_app";
        // Lozinke dolaze iz okruženja. Ako ih nema, pokušavamo sa ZATEČENIM lozinkama iz postavljanja laboratorija –
        // ako one još rade, to je nalaz (zadatak Z2.1), a ne pogodnost.
        zatecenaLozinka = okolina("APP_LOZINKA", "").isEmpty();
        appLozinka = okolina("APP_LOZINKA", domena + "123");
        podrskaLozinka = okolina("PODRSKA_LOZINKA", "Sluzba-Pomoci24");

        IZLAZ.println("=== Aplikacija i baza: što smije aplikacijski račun ===");
        IZLAZ.println("Domena: " + domena + " | baza: " + d.baza() + " | prijava: " + app
                + " | poslužitelj: " + host + "," + port);
        IZLAZ.println("Veza: šifrirana (Encrypt=yes); certifikat poslužitelja se ne provjerava samo u laboratoriju.");

        try {
            try (Connection veza = spoji(app, appLozinka)) {
                tkoSam(veza);
                stoMogu(veza);
            } catch (SQLException greska) {
                if (REZULTATI.isEmpty()) {
                    IZLAZ.println();
                    IZLAZ.println("Ne mogu se spojiti kao " + app + ": " + prviRedak(greska, 200));
                    IZLAZ.println("Provjerite radi li poslužitelj (docker compose ps). Ako ste u zadatku Z2.1 promijenili");
                    IZLAZ.println("lozinku aplikacijske prijave, upišite je u .env kao APP_LOZINKA=... (ne u kod!).");
                    return 2;
                }
                throw greska;
            }
            injekcija();
            rls();
            podrska();
        } catch (SQLException greska) {
            IZLAZ.println("Neočekivana greška baze: " + prviRedak(greska, 300));
            return 3;
        }

        IZLAZ.println();
        if (upozorenja > 0) {
            IZLAZ.println("Upozorenja: " + upozorenja + ". Aplikacijski račun (ili podrška) smije više nego što treba –");
            IZLAZ.println("riješite zadatke Z2–Z4 iz ZADACI.md i pokrenite demo ponovno.");
        } else {
            IZLAZ.println("Upozorenja: 0. Aplikacija radi s najmanjim ovlastima, a baza je druga linija obrane.");
        }
        rezultat("upozorenja", String.valueOf(upozorenja));
        IZLAZ.println();
        for (String[] r : REZULTATI) {
            IZLAZ.println("DEMO|" + r[0] + "|" + r[1]);
        }
        return upozorenja > 0 && "1".equals(System.getenv("DEMO_STROGO")) ? 1 : 0;
    }

    private static void tkoSam(Connection veza) throws SQLException {
        IZLAZ.println();
        IZLAZ.println("1. Tko sam u bazi");
        try (Statement st = veza.createStatement();
                ResultSet rs = st.executeQuery("SELECT ORIGINAL_LOGIN(), USER_NAME(), IS_SRVROLEMEMBER('sysadmin'), "
                        + "IS_ROLEMEMBER('db_owner'), IS_ROLEMEMBER('uloga_aplikacija')")) {
            rs.next();
            boolean sysadmin = rs.getInt(3) == 1;
            boolean dbOwner = rs.getInt(4) == 1;
            boolean uloga = rs.getInt(5) == 1; // NULL (uloga ne postoji) -> 0
            ispis("prijava (login)", rs.getString(1), "");
            ispis("korisnik u bazi", rs.getString(2), "");
            ispis("lozinka", zatecenaLozinka ? "zatečena" : "iz varijable okruženja",
                    zatecenaLozinka ? "prijava radi sa zatečenom lozinkom iz postavljanja (Z2.1)" : "");
            ispis("član sysadmin", daNe(sysadmin), sysadmin ? "aplikacija je administrator poslužitelja (Z2.2)" : "");
            ispis("član db_owner", daNe(dbOwner), dbOwner ? "aplikacija je vlasnik baze (Z2.3)" : "");
            ispis("član uloga_aplikacija", daNe(uloga), uloga ? "" : "nema vlastite uloge s minimalnim pravima (Z3.1)");
            rezultat("lozinka", zatecenaLozinka ? "ZATECENA" : "IZ_OKRUZENJA");
            rezultat("sysadmin", daNe(sysadmin));
            rezultat("db_owner", daNe(dbOwner));
            rezultat("uloga_aplikacija", daNe(uloga));
        }
        veza.rollback();
    }

    private static void stoMogu(Connection veza) throws SQLException {
        IZLAZ.println();
        IZLAZ.println("2. Što račun stvarno može (pokušaji se poništavaju – ROLLBACK)");
        boolean uspjelo = pokusaj(veza, "SELECT COUNT(*) FROM dbo.revizija");
        ispis("čitanje dnevnika dbo.revizija", uspjelo ? "DOPUŠTENO" : "ODBIJENO",
                uspjelo ? "aplikacija može čitati (i brisati) vlastite tragove (Z3.3)" : "");
        rezultat("revizija", uspjelo ? "DOPUSTENO" : "ODBIJENO");
        byte[] nasumicno = new byte[4];
        new SecureRandom().nextBytes(nasumicno);
        String proba = "demo_proba_" + HexFormat.of().formatHex(nasumicno); // naziv stvaramo sami – nije korisnički unos
        uspjelo = pokusaj(veza, "CREATE TABLE dbo." + proba + " (id INT)");
        ispis("CREATE TABLE (promjena sheme)", uspjelo ? "DOPUŠTENO" : "ODBIJENO",
                uspjelo ? "aplikacija smije mijenjati shemu – i napadač kroz SQL injection (Z3.2)" : "");
        rezultat("ddl", uspjelo ? "DOPUSTENO" : "ODBIJENO");
    }

    private static void injekcija() throws SQLException {
        IZLAZ.println();
        IZLAZ.println("3. Isti unos na dva načina (sesija korisnika ana, unos: " + ZLONAMJERNI_UNOS + ")");
        try (Connection veza = kaoKorisnik("ana")) {
            // ISPRAVNO: unos putuje kao parametar – baza ga nikad ne tumači kao SQL.
            long kaoParametar = vrijednost(veza,
                    "SELECT COUNT(*) FROM dbo." + d.glavna() + " WHERE " + d.vlasnik() + " = ?", ZLONAMJERNI_UNOS);
            ispis("parametar (?)", redaka(kaoParametar), "", "unos je ostao podatak");
            // POGREŠNO (samo za demonstraciju): unos zalijepljen u tekst upita postaje dio naredbe.
            String zalijepljeno = "SELECT COUNT(*) FROM dbo." + d.glavna() + " WHERE " + d.vlasnik()
                    + " = N'" + ZLONAMJERNI_UNOS + "'";
            long svi = vrijednost(veza, zalijepljeno);
            long tudji = vrijednost(veza,
                    "SELECT COUNT(*) FROM dbo." + d.glavna() + " WHERE " + d.vlasnik() + " <> ?", "ana");
            ispis("lijepljenje u tekst upita", redaka(svi),
                    tudji > 0 ? "injekcija vraća i tuđe zapise – baza ih ne filtrira (Z4.2)" : "",
                    "injekcija uspijeva, ali RLS vraća samo Anine zapise – obrana u dubinu");
            rezultat("parametar", String.valueOf(kaoParametar));
            rezultat("injekcija_tudji", String.valueOf(tudji));
        }
    }

    private static void rls() throws SQLException {
        IZLAZ.println();
        IZLAZ.println("4. Row-Level Security: SESSION_CONTEXT(N'korisnik') nad dbo." + d.glavna());
        for (String korisnik : new String[] {"ana", "marko", null}) {
            try (Connection veza = kaoKorisnik(korisnik)) {
                long svi = vrijednost(veza, "SELECT COUNT(*) FROM dbo." + d.glavna());
                if (korisnik == null) {
                    ispis("bez prijavljenog korisnika", "vidi " + redaka(svi),
                            svi > 0 ? "bez konteksta aplikacija ne smije vidjeti ništa (Z4.2)" : "");
                    rezultat("rls_bez", String.valueOf(svi));
                } else {
                    long tudji = vrijednost(veza,
                            "SELECT COUNT(*) FROM dbo." + d.glavna() + " WHERE " + d.vlasnik() + " <> ?", korisnik);
                    ispis("korisnik " + korisnik, "vidi " + redaka(svi) + ", od toga tuđih: " + tudji,
                            tudji > 0 ? "vidi tuđe zapise (Z4.1, Z4.2)" : "");
                    rezultat("rls_" + korisnik + "_tudji", String.valueOf(tudji));
                }
            }
        }
    }

    private static void podrska() throws SQLException {
        IZLAZ.println();
        IZLAZ.println("5. Korisnička podrška (prijava podrska): maskiranje i najmanje ovlasti");
        Connection veza;
        try {
            veza = spoji("podrska", podrskaLozinka);
        } catch (SQLException neuspjelaPrijava) {
            IZLAZ.println("   preskočeno – prijava podrska nije uspjela (ako ste joj promijenili lozinku,");
            IZLAZ.println("   postavite PODRSKA_LOZINKA)");
            rezultat("podrska_oib", "PRESKOCENO");
            rezultat("podrska_hash", "PRESKOCENO");
            return;
        }
        try (veza) {
            try (PreparedStatement ps = veza.prepareStatement(
                    "SELECT TOP (1) oib, email FROM dbo.korisnici WHERE username = ?")) {
                ps.setString(1, "ana");
                try (ResultSet rs = ps.executeQuery()) {
                    rs.next();
                    String oib = rs.getString(1);
                    boolean vidljiv = oib != null && oib.matches("\\d{11}");
                    ispis("OIB i e-mail korisnice ana", oib + " · " + rs.getString(2),
                            vidljiv ? "podrška vidi pune osobne podatke (Z4.3, Z4.4)" : "", "maskirano");
                    rezultat("podrska_oib", vidljiv ? "VIDLJIV" : "MASKIRAN");
                }
            } catch (SQLException greska) {
                ispis("OIB i e-mail korisnice ana", "ODBIJENO",
                        "podrška mora moći čitati korisnike (Z4.4): " + prviRedak(greska, 60));
                rezultat("podrska_oib", "ODBIJENO");
            }
            veza.rollback();
            boolean uspjelo = pokusaj(veza, "SELECT TOP (1) password_hash FROM dbo.korisnici");
            ispis("čitanje password_hash", uspjelo ? "DOPUŠTENO" : "ODBIJENO",
                    uspjelo ? "podrška može čitati hasheve lozinki (Z2.5, Z4.5)" : "");
            rezultat("podrska_hash", uspjelo ? "DOPUSTENO" : "ODBIJENO");
        }
    }
}
