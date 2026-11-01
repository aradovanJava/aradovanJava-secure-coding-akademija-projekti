using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using Ulaznica.Api.Infrastruktura;
// @@VULN S11
// @@SECURE S11
using Microsoft.AspNetCore.WebUtilities;
// @@END S11

namespace Ulaznica.Api.Autentikacija;

public enum RezultatPromjeneLozinke
{
    Promijenjena,
    NeispravanToken,
    PrekratkaLozinka,
}

/// <summary>Obnova zaboravljene lozinke: token se šalje e-poštom, a zatim se njime postavlja nova lozinka.</summary>
public sealed class ResetLozinkeServis(
    Baza baza, KorisniciServis korisnici, Posta posta, PostavkeAplikacije postavke, ILogger<ResetLozinkeServis> logger)
{
    public const int NajmanjaDuljinaLozinke = 8;
// @@VULN S11
// @@SECURE S11
    private static readonly TimeSpan TrajanjeTokena = TimeSpan.FromMinutes(15);
// @@END S11

    public void ZatraziPromjenu(string? username)
    {
        var korisnik = string.IsNullOrWhiteSpace(username) ? null : korisnici.PronadjiPoKorisnickomImenu(username.Trim());
        if (korisnik is null)
        {
            logger.LogInformation("Zahtjev za obnovu lozinke za nepostojeći račun");
            return;
        }

// @@VULN S11
        var datum = DateTime.Now.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
        var token = Convert.ToHexString(MD5.HashData(Encoding.UTF8.GetBytes(korisnik.Username + datum))).ToLowerInvariant();
        baza.Izvrsi(
            "INSERT INTO reset_tokeni (token, korisnik_id, kreirano) VALUES ($t, $k, $c)",
            ("$t", token), ("$k", korisnik.Id), ("$c", DateTime.UtcNow.ToString("O", CultureInfo.InvariantCulture)));
// @@SECURE S11
        var token = WebEncoders.Base64UrlEncode(RandomNumberGenerator.GetBytes(32));
        baza.Izvrsi(
            "INSERT INTO reset_tokeni (token_hash, korisnik_id, vrijedi_do, iskoristen) VALUES ($h, $k, $v, 0)",
            ("$h", Sazetak(token)), ("$k", korisnik.Id), ("$v", DateTimeOffset.UtcNow.Add(TrajanjeTokena).ToUnixTimeSeconds()));
// @@END S11

        posta.Posalji(korisnik.Username, korisnik.Email, "Obnova lozinke", $"""
            Poštovani,

            zatražena je obnova lozinke za korisnički račun {korisnik.Username}.
            Novu lozinku možete postaviti na poveznici:
            {postavke.JavniUrl}/reset?token={Uri.EscapeDataString(token)}

            Token: {token}

            Ako niste zatražili obnovu lozinke, zanemarite ovu poruku.
            """);
        logger.LogInformation("Poslane su upute za obnovu lozinke korisniku {Username}", korisnik.Username);
    }

    public RezultatPromjeneLozinke PromijeniLozinku(string? token, string? novaLozinka)
    {
        if (string.IsNullOrWhiteSpace(token))
        {
            return RezultatPromjeneLozinke.NeispravanToken;
        }
        if (novaLozinka is null || novaLozinka.Length < NajmanjaDuljinaLozinke)
        {
            return RezultatPromjeneLozinke.PrekratkaLozinka;
        }

        using var veza = baza.Otvori();
// @@VULN S11
        var zapis = Baza.Upit(veza, null,
            "SELECT korisnik_id FROM reset_tokeni WHERE token = $t", ("$t", token.Trim())).FirstOrDefault();
        if (zapis is null)
        {
            return RezultatPromjeneLozinke.NeispravanToken;
        }
        var korisnikId = zapis.Broj("korisnik_id");
        korisnici.PostaviLozinku(veza, null, korisnikId, novaLozinka);
// @@SECURE S11
        using var transakcija = veza.BeginTransaction();
        var zapis = Baza.Upit(veza, transakcija,
            "SELECT id, korisnik_id FROM reset_tokeni WHERE token_hash = $h AND iskoristen = 0 AND vrijedi_do > $sada",
            ("$h", Sazetak(token.Trim())), ("$sada", DateTimeOffset.UtcNow.ToUnixTimeSeconds())).FirstOrDefault();
        if (zapis is null)
        {
            return RezultatPromjeneLozinke.NeispravanToken;
        }
        var korisnikId = zapis.Broj("korisnik_id");
        Baza.Izvrsi(veza, transakcija, "UPDATE reset_tokeni SET iskoristen = 1 WHERE korisnik_id = $k", ("$k", korisnikId));
        korisnici.PostaviLozinku(veza, transakcija, korisnikId, novaLozinka);
        transakcija.Commit();
// @@END S11

        logger.LogInformation("Promijenjena je lozinka korisnika s ID-om {Id}", korisnikId);
        return RezultatPromjeneLozinke.Promijenjena;
    }
// @@VULN S11
// @@SECURE S11

    private static string Sazetak(string token) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(token)));
// @@END S11
}
