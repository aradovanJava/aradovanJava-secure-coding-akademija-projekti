// Demo „Aplikacija i baza” (C#, ADO.NET): što aplikacijski račun smije u bazi.
//
// Program se spaja na SQL Server iz laboratorija ONAKO KAKO SE SPAJA APLIKACIJA: prijavom <domena>_app (ne sa!),
// šifriranom vezom, lozinkom iz varijable okruženja (nikad iz koda ni iz repozitorija), isključivo parametriziranim
// upitima, i na početku „zahtjeva” postavlja SESSION_CONTEXT s prijavljenim korisnikom (za Row-Level Security).
// Zatim ispisuje što taj račun stvarno smije. Pokrenite ga PRIJE zadataka (zatečeno stanje) i POSLIJE zadataka
// Z2–Z4: upozorenja [!] moraju nestati.
//
// Pokretanje (README.md, odjeljak „Demo: aplikacija i baza”):
//   docker compose --profile aplikacija run --rm aplikacija-dotnet
// ili lokalno (.NET 10 SDK):  dotnet run
// Postavke (varijable okruženja): DOMENA, SQL_HOST, SQL_PORT, APP_LOZINKA, PODRSKA_LOZINKA.
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Data.SqlClient;

Console.OutputEncoding = Encoding.UTF8; // dijakritici i na Windows konzoli

// Nazivi tablica i stupaca NE MOGU biti parametri upita, zato dolaze isključivo iz ovog popisa dopuštenih
// vrijednosti – nikad iz korisničkog unosa (usporedi S08 iz T2).
var domene = new Dictionary<string, (string Baza, string Glavna, string Vlasnik)>
{
    ["medtermin"] = ("MedTermin", "rezervacije", "pacijent"),
    ["ulaznica"] = ("Ulaznica", "narudzbe", "kupac"),
    ["kadrovska"] = ("Kadrovska", "zahtjevi", "zaposlenik"),
};
const string ZlonamjerniUnos = "x' OR 1=1 --";

static string Okolina(string ime, string zadano)
{
    var v = Environment.GetEnvironmentVariable(ime);
    return string.IsNullOrWhiteSpace(v) ? zadano : v;
}

var domena = Okolina("DOMENA", "medtermin").Trim().ToLowerInvariant();
if (!domene.TryGetValue(domena, out var d))
{
    Console.WriteLine($"DOMENA mora biti medtermin, ulaznica ili kadrovska (sada: '{domena}').");
    return 2;
}
var host = Okolina("SQL_HOST", "localhost");
var port = Okolina("SQL_PORT", "1433");
var app = $"{domena}_app";
// Lozinke dolaze iz okruženja. Ako ih nema, pokušavamo sa ZATEČENIM lozinkama iz postavljanja laboratorija –
// ako one još rade, to je nalaz (zadatak Z2.1), a ne pogodnost.
var zatecenaLozinka = Okolina("APP_LOZINKA", "").Length == 0;
var appLozinka = Okolina("APP_LOZINKA", $"{domena}123");
var podrskaLozinka = Okolina("PODRSKA_LOZINKA", "Sluzba-Pomoci24");

var upozorenja = 0;
var rezultati = new List<(string Kljuc, string Stanje)>(); // strojno čitljivi sažetak (DEMO|ključ|vrijednost)

// Nova veza. Encrypt=True: promet je šifriran (TLS). TrustServerCertificate=True smije stajati SAMO u laboratoriju
// (samopotpisani certifikat poslužitelja); u produkciji certifikat kojem klijent vjeruje.
SqlConnection Spoji(string prijava, string lozinka)
{
    var niz = new SqlConnectionStringBuilder // builder: lozinka smije sadržavati ; i = bez lomljenja niza
    {
        DataSource = $"{host},{port}",
        InitialCatalog = d.Baza,
        UserID = prijava,
        Password = lozinka,
        Encrypt = SqlConnectionEncryptOption.Mandatory,
        TrustServerCertificate = true,
        ConnectTimeout = 15,
        Pooling = false, // svaka veza je zaseban „zahtjev” s vlastitim SESSION_CONTEXT-om
    };
    var veza = new SqlConnection(niz.ConnectionString);
    veza.Open();
    return veza;
}

// Veza aplikacije za jedan „zahtjev”: nakon prijave korisnika aplikacija bazi kaže tko je on.
SqlConnection KaoKorisnik(string? korisnik)
{
    var veza = Spoji(app, appLozinka);
    if (korisnik is not null)
    {
        // @read_only = 1: kasniji kod (pa ni SQL injection) u istoj sesiji više ne može promijeniti identitet.
        using var cmd = new SqlCommand(
            "EXEC sp_set_session_context @key = N'korisnik', @value = @korisnik, @read_only = 1", veza);
        cmd.Parameters.Add("@korisnik", System.Data.SqlDbType.NVarChar, 50).Value = korisnik;
        cmd.ExecuteNonQuery();
    }
    return veza;
}

// Prvi stupac prvog retka. Parametri se šalju odvojeno od teksta upita (@p0, @p1 …).
static long Vrijednost(SqlConnection veza, string upit, params string[] parametri)
{
    using var cmd = new SqlCommand(upit, veza);
    for (var i = 0; i < parametri.Length; i++)
    {
        cmd.Parameters.Add($"@p{i}", System.Data.SqlDbType.NVarChar, 100).Value = parametri[i];
    }
    return Convert.ToInt64(cmd.ExecuteScalar());
}

// true ako baza dopusti naredbu; pokušaj se uvijek poništava (i CREATE TABLE je dio transakcije).
static bool Pokusaj(SqlConnection veza, string naredba)
{
    using var tx = veza.BeginTransaction();
    try
    {
        using var cmd = new SqlCommand(naredba, veza, tx);
        cmd.ExecuteNonQuery();
        return true;
    }
    catch (SqlException)
    {
        return false;
    }
    finally
    {
        if (tx.Connection is not null)
        {
            tx.Rollback(); // ništa od pokušaja ne ostaje u bazi
        }
    }
}

static string Redaka(long n) =>
    n % 10 == 1 && n % 100 != 11 ? $"{n} redak"
    : n % 10 is >= 2 and <= 4 && (n % 100 < 12 || n % 100 > 14) ? $"{n} retka"
    : $"{n} redaka";

void Ispis(string opis, string stanje, string upozorenje = "", string napomena = "")
{
    var dodatak = "";
    if (upozorenje.Length > 0)
    {
        upozorenja++;
        dodatak = $"  [!] {upozorenje}";
    }
    else if (napomena.Length > 0)
    {
        dodatak = $"  ({napomena})";
    }
    Console.WriteLine($"   {(opis + " ").PadRight(36, '.')} {stanje}{dodatak}");
}

static string DaNe(bool uvjet) => uvjet ? "DA" : "NE";
static string PrviRedak(Exception e, int najvise)
{
    var p = e.Message.Split('\n')[0];
    return p.Length > najvise ? p[..najvise] : p;
}

Console.WriteLine("=== Aplikacija i baza: što smije aplikacijski račun ===");
Console.WriteLine($"Domena: {domena} | baza: {d.Baza} | prijava: {app} | poslužitelj: {host},{port}");
Console.WriteLine("Veza: šifrirana (Encrypt=yes); certifikat poslužitelja se ne provjerava samo u laboratoriju.");

SqlConnection prva;
try
{
    prva = Spoji(app, appLozinka);
}
catch (SqlException greska)
{
    Console.WriteLine();
    Console.WriteLine($"Ne mogu se spojiti kao {app}: {PrviRedak(greska, 200)}");
    Console.WriteLine("Provjerite radi li poslužitelj (docker compose ps). Ako ste u zadatku Z2.1 promijenili");
    Console.WriteLine("lozinku aplikacijske prijave, upišite je u .env kao APP_LOZINKA=... (ne u kod!).");
    return 2;
}

try
{
    using (var veza = prva)
    {
        Console.WriteLine();
        Console.WriteLine("1. Tko sam u bazi");
        using (var cmd = new SqlCommand(
            "SELECT ORIGINAL_LOGIN(), USER_NAME(), IS_SRVROLEMEMBER('sysadmin'), "
            + "IS_ROLEMEMBER('db_owner'), IS_ROLEMEMBER('uloga_aplikacija')", veza))
        using (var r = cmd.ExecuteReader())
        {
            r.Read();
            static bool Clan(object o) => o is not DBNull && Convert.ToInt32(o) == 1; // NULL (uloga ne postoji) -> ne
            var sysadmin = Clan(r.GetValue(2));
            var dbOwner = Clan(r.GetValue(3));
            var uloga = Clan(r.GetValue(4));
            Ispis("prijava (login)", r.GetString(0));
            Ispis("korisnik u bazi", r.GetString(1));
            Ispis("lozinka", zatecenaLozinka ? "zatečena" : "iz varijable okruženja",
                zatecenaLozinka ? "prijava radi sa zatečenom lozinkom iz postavljanja (Z2.1)" : "");
            Ispis("član sysadmin", DaNe(sysadmin), sysadmin ? "aplikacija je administrator poslužitelja (Z2.2)" : "");
            Ispis("član db_owner", DaNe(dbOwner), dbOwner ? "aplikacija je vlasnik baze (Z2.3)" : "");
            Ispis("član uloga_aplikacija", DaNe(uloga), uloga ? "" : "nema vlastite uloge s minimalnim pravima (Z3.1)");
            rezultati.Add(("lozinka", zatecenaLozinka ? "ZATECENA" : "IZ_OKRUZENJA"));
            rezultati.Add(("sysadmin", DaNe(sysadmin)));
            rezultati.Add(("db_owner", DaNe(dbOwner)));
            rezultati.Add(("uloga_aplikacija", DaNe(uloga)));
        }

        Console.WriteLine();
        Console.WriteLine("2. Što račun stvarno može (pokušaji se poništavaju – ROLLBACK)");
        var uspjelo = Pokusaj(veza, "SELECT COUNT(*) FROM dbo.revizija");
        Ispis("čitanje dnevnika dbo.revizija", uspjelo ? "DOPUŠTENO" : "ODBIJENO",
            uspjelo ? "aplikacija može čitati (i brisati) vlastite tragove (Z3.3)" : "");
        rezultati.Add(("revizija", uspjelo ? "DOPUSTENO" : "ODBIJENO"));
        var proba = "demo_proba_" + Convert.ToHexString(RandomNumberGenerator.GetBytes(4)).ToLowerInvariant(); // naziv stvaramo sami
        uspjelo = Pokusaj(veza, $"CREATE TABLE dbo.{proba} (id INT)");
        Ispis("CREATE TABLE (promjena sheme)", uspjelo ? "DOPUŠTENO" : "ODBIJENO",
            uspjelo ? "aplikacija smije mijenjati shemu – i napadač kroz SQL injection (Z3.2)" : "");
        rezultati.Add(("ddl", uspjelo ? "DOPUSTENO" : "ODBIJENO"));
    }

    Console.WriteLine();
    Console.WriteLine($"3. Isti unos na dva načina (sesija korisnika ana, unos: {ZlonamjerniUnos})");
    using (var veza = KaoKorisnik("ana"))
    {
        // ISPRAVNO: unos putuje kao parametar – baza ga nikad ne tumači kao SQL.
        var kaoParametar = Vrijednost(veza, $"SELECT COUNT(*) FROM dbo.{d.Glavna} WHERE {d.Vlasnik} = @p0", ZlonamjerniUnos);
        Ispis("parametar (@p0)", Redaka(kaoParametar), napomena: "unos je ostao podatak");
        // POGREŠNO (samo za demonstraciju): unos zalijepljen u tekst upita postaje dio naredbe.
        var zalijepljeno = $"SELECT COUNT(*) FROM dbo.{d.Glavna} WHERE {d.Vlasnik} = N'{ZlonamjerniUnos}'";
        var svi = Vrijednost(veza, zalijepljeno);
        var tudji = Vrijednost(veza, $"SELECT COUNT(*) FROM dbo.{d.Glavna} WHERE {d.Vlasnik} <> @p0", "ana");
        Ispis("lijepljenje u tekst upita", Redaka(svi),
            tudji > 0 ? "injekcija vraća i tuđe zapise – baza ih ne filtrira (Z4.2)" : "",
            "injekcija uspijeva, ali RLS vraća samo Anine zapise – obrana u dubinu");
        rezultati.Add(("parametar", kaoParametar.ToString()));
        rezultati.Add(("injekcija_tudji", tudji.ToString()));
    }

    Console.WriteLine();
    Console.WriteLine($"4. Row-Level Security: SESSION_CONTEXT(N'korisnik') nad dbo.{d.Glavna}");
    foreach (var korisnik in new string?[] { "ana", "marko", null })
    {
        using var veza = KaoKorisnik(korisnik);
        var svi = Vrijednost(veza, $"SELECT COUNT(*) FROM dbo.{d.Glavna}");
        if (korisnik is null)
        {
            Ispis("bez prijavljenog korisnika", $"vidi {Redaka(svi)}",
                svi > 0 ? "bez konteksta aplikacija ne smije vidjeti ništa (Z4.2)" : "");
            rezultati.Add(("rls_bez", svi.ToString()));
        }
        else
        {
            var tudji = Vrijednost(veza, $"SELECT COUNT(*) FROM dbo.{d.Glavna} WHERE {d.Vlasnik} <> @p0", korisnik);
            Ispis($"korisnik {korisnik}", $"vidi {Redaka(svi)}, od toga tuđih: {tudji}",
                tudji > 0 ? "vidi tuđe zapise (Z4.1, Z4.2)" : "");
            rezultati.Add(($"rls_{korisnik}_tudji", tudji.ToString()));
        }
    }

    Console.WriteLine();
    Console.WriteLine("5. Korisnička podrška (prijava podrska): maskiranje i najmanje ovlasti");
    SqlConnection? podrska = null;
    try
    {
        podrska = Spoji("podrska", podrskaLozinka);
    }
    catch (SqlException)
    {
        Console.WriteLine("   preskočeno – prijava podrska nije uspjela (ako ste joj promijenili lozinku,");
        Console.WriteLine("   postavite PODRSKA_LOZINKA)");
        rezultati.Add(("podrska_oib", "PRESKOCENO"));
        rezultati.Add(("podrska_hash", "PRESKOCENO"));
    }
    if (podrska is not null)
    {
        using (podrska)
        {
            try
            {
                using var cmd = new SqlCommand("SELECT TOP (1) oib, email FROM dbo.korisnici WHERE username = @korisnik", podrska);
                cmd.Parameters.Add("@korisnik", System.Data.SqlDbType.NVarChar, 50).Value = "ana";
                using var r = cmd.ExecuteReader();
                r.Read();
                var oib = r.IsDBNull(0) ? "" : r.GetString(0);
                var email = r.IsDBNull(1) ? "" : r.GetString(1);
                var vidljiv = Regex.IsMatch(oib, @"^\d{11}$");
                Ispis("OIB i e-mail korisnice ana", $"{oib} · {email}",
                    vidljiv ? "podrška vidi pune osobne podatke (Z4.3, Z4.4)" : "", "maskirano");
                rezultati.Add(("podrska_oib", vidljiv ? "VIDLJIV" : "MASKIRAN"));
            }
            catch (SqlException greska)
            {
                Ispis("OIB i e-mail korisnice ana", "ODBIJENO",
                    $"podrška mora moći čitati korisnike (Z4.4): {PrviRedak(greska, 60)}");
                rezultati.Add(("podrska_oib", "ODBIJENO"));
            }
            var uspjelo = Pokusaj(podrska, "SELECT TOP (1) password_hash FROM dbo.korisnici");
            Ispis("čitanje password_hash", uspjelo ? "DOPUŠTENO" : "ODBIJENO",
                uspjelo ? "podrška može čitati hasheve lozinki (Z2.5, Z4.5)" : "");
            rezultati.Add(("podrska_hash", uspjelo ? "DOPUSTENO" : "ODBIJENO"));
        }
    }
}
catch (SqlException greska)
{
    Console.WriteLine($"Neočekivana greška baze: {PrviRedak(greska, 300)}");
    return 3;
}

Console.WriteLine();
if (upozorenja > 0)
{
    Console.WriteLine($"Upozorenja: {upozorenja}. Aplikacijski račun (ili podrška) smije više nego što treba –");
    Console.WriteLine("riješite zadatke Z2–Z4 iz ZADACI.md i pokrenite demo ponovno.");
}
else
{
    Console.WriteLine("Upozorenja: 0. Aplikacija radi s najmanjim ovlastima, a baza je druga linija obrane.");
}
rezultati.Add(("upozorenja", upozorenja.ToString()));
Console.WriteLine();
foreach (var (kljuc, stanje) in rezultati)
{
    Console.WriteLine($"DEMO|{kljuc}|{stanje}");
}
return upozorenja > 0 && Environment.GetEnvironmentVariable("DEMO_STROGO") == "1" ? 1 : 0;
