// @@VULN S09
// @@SECURE S09
using System.Text.Encodings.Web;
// @@END S09
using Microsoft.AspNetCore.Mvc;
using Ulaznica.Api.Autentikacija;
using Ulaznica.Api.Infrastruktura;

namespace Ulaznica.Api.Prodaja;

/// <summary>HTML ulaznice za ispis.</summary>
[PotrebnaPrijava]
public sealed class IspisController(Baza baza) : ControllerBase
{
    [HttpGet("/ispis/narudzbe/{id:long}")]
    public IActionResult IspisUlaznice(long id)
    {
        var korisnik = HttpContext.Korisnik();
        var n = baza.Upit("""
            SELECT n.id, n.kupac, n.kolicina, n.ime_na_ulaznici, n.kreirano, d.naziv, d.mjesto, d.datum, d.cijena
            FROM narudzbe n JOIN dogadjaji d ON d.id = n.dogadjaj_id
            WHERE n.id = $id
            """, ("$id", id)).FirstOrDefault();
        if (n is null || (n.Tekst("kupac") != korisnik.Username && !korisnik.JeAdmin))
        {
            return NotFound(new { greska = "Narudžba ne postoji." });
        }

        var datum = n.Tekst("datum").Replace('T', ' ');
        var kod = $"UL-{n.Broj("id"):D6}";
// @@VULN S09
        var tijelo = $"""
            <h1>{n.Tekst("naziv")}</h1>
            <table>
            <tr><th>Ime na ulaznici</th><td>{n.Tekst("ime_na_ulaznici")}</td></tr>
            <tr><th>Mjesto</th><td>{n.Tekst("mjesto")}</td></tr>
            <tr><th>Datum i vrijeme</th><td>{datum}</td></tr>
            <tr><th>Broj ulaznica</th><td>{n.Broj("kolicina")}</td></tr>
            <tr><th>Kod ulaznice</th><td><strong>{kod}</strong></td></tr>
            </table>
            <p>Ulaznicu pokažite na ulazu (ispisanu ili na mobitelu). Kupljeno: {n.Tekst("kreirano")}</p>
            """;
// @@SECURE S09
        var tijelo = $"""
            <h1>{H(n.Tekst("naziv"))}</h1>
            <table>
            <tr><th>Ime na ulaznici</th><td>{H(n.Tekst("ime_na_ulaznici"))}</td></tr>
            <tr><th>Mjesto</th><td>{H(n.Tekst("mjesto"))}</td></tr>
            <tr><th>Datum i vrijeme</th><td>{H(datum)}</td></tr>
            <tr><th>Broj ulaznica</th><td>{n.Broj("kolicina")}</td></tr>
            <tr><th>Kod ulaznice</th><td><strong>{H(kod)}</strong></td></tr>
            </table>
            <p>Ulaznicu pokažite na ulazu (ispisanu ili na mobitelu). Kupljeno: {H(n.Tekst("kreirano"))}</p>
            """;
        Response.Headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'";
// @@END S09
        return HtmlStranica.Odgovor($"Ulaznica {kod}", tijelo);
    }
// @@VULN S09
// @@SECURE S09

    private static string H(string tekst) => HtmlEncoder.Default.Encode(tekst);
// @@END S09
}
