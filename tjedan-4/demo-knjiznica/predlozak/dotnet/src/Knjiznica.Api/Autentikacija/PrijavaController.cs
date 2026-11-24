using System.Text.RegularExpressions;
using Knjiznica.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace Knjiznica.Api.Autentikacija;

/// <summary>Prijava i registracija članova.</summary>
[ApiController]
public sealed partial class PrijavaController(Baza baza, Lozinke lozinke, Tokeni tokeni, ILogger<PrijavaController> logger)
    : ControllerBase
{
    public sealed record PrijavaZahtjev(string? KorisnickoIme, string? Lozinka);

    public sealed record RegistracijaZahtjev(string? KorisnickoIme, string? Lozinka, string? Ime, string? Email);

    [GeneratedRegex("^[a-z0-9._-]{3,40}$")]
    private static partial Regex KorisnickoImeRegex();

    [HttpPost("/api/prijava")]
    public IActionResult Prijava(PrijavaZahtjev zahtjev)
    {
        if (zahtjev.KorisnickoIme is null || zahtjev.Lozinka is null)
        {
            return Greska.Neispravno("Neispravan zahtjev.");
        }
        var ip = HttpContext.Connection.RemoteIpAddress?.ToString() ?? "-";
        var racun = baza.Jedan(
            "SELECT id, korisnicko_ime, uloga, lozinka_hash FROM korisnici WHERE korisnicko_ime = $ime",
            ("$ime", zahtjev.KorisnickoIme));
        // @@VULN K07
        logger.LogInformation("Prijava korisnika {Korisnik} (lozinka: {Lozinka}) s adrese {Ip}",
            zahtjev.KorisnickoIme, zahtjev.Lozinka, ip);
        if (racun is null || !lozinke.Provjeri(zahtjev.Lozinka, (string)racun["lozinka_hash"]!))
        {
            return Greska.NeispravnaPrijava();
        }
        // @@SECURE K07
        if (racun is null || !lozinke.Provjeri(zahtjev.Lozinka, (string)racun["lozinka_hash"]!))
        {
            logger.LogWarning("SECURITY_EVENT LOGIN_FAILED korisnik={Korisnik} ip={Ip}", Ocisti(zahtjev.KorisnickoIme), ip);
            return Greska.NeispravnaPrijava();
        }
        logger.LogInformation("SECURITY_EVENT LOGIN_SUCCESS korisnik={Korisnik} ip={Ip}",
            Ocisti((string)racun["korisnicko_ime"]!), ip);
        // @@END K07
        return Ok(new
        {
            token = tokeni.Izdaj((long)racun["id"]!),
            korisnickoIme = (string)racun["korisnicko_ime"]!,
            uloga = (string)racun["uloga"]!,
        });
    }
    // @@VULN K07
    // @@SECURE K07

    /// <summary>Neutralizira znakove za novi red da korisnički unos ne može krivotvoriti zapis u dnevniku.</summary>
    private static string Ocisti(string tekst) => tekst.Replace('\r', '_').Replace('\n', '_');
    // @@END K07

    [HttpPost("/api/registracija")]
    public IActionResult Registracija(RegistracijaZahtjev zahtjev)
    {
        if (zahtjev.KorisnickoIme is null || !KorisnickoImeRegex().IsMatch(zahtjev.KorisnickoIme)
            || zahtjev.Lozinka is null || zahtjev.Lozinka.Length < 8
            || string.IsNullOrWhiteSpace(zahtjev.Ime)
            || zahtjev.Email is null || !zahtjev.Email.Contains('@'))
        {
            return Greska.Neispravno("Neispravni podaci za registraciju.");
        }
        if (baza.Jedan("SELECT id FROM korisnici WHERE korisnicko_ime = $ime", ("$ime", zahtjev.KorisnickoIme)) is not null)
        {
            return Greska.Sukob("Korisničko ime je zauzeto.");
        }
        var id = baza.Umetni(
            "INSERT INTO korisnici (korisnicko_ime, lozinka_hash, uloga, ime, email) VALUES ($ime, $hash, 'CLAN', $puno, $email)",
            ("$ime", zahtjev.KorisnickoIme), ("$hash", lozinke.Hashiraj(zahtjev.Lozinka)),
            ("$puno", zahtjev.Ime.Trim()), ("$email", zahtjev.Email.Trim()));
        return StatusCode(201, new { id });
    }
}
