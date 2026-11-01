// @@VULN S09
// @@SECURE S09
using System.Text.Encodings.Web;
// @@END S09
using MedTermin.Api.Autentikacija;
using MedTermin.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace MedTermin.Api.Poliklinika;

/// <summary>HTML potvrde za ispis.</summary>
[PotrebnaPrijava]
public sealed class IspisController(Baza baza) : ControllerBase
{
    [HttpGet("/ispis/rezervacije/{id:long}")]
    public IActionResult Rezervacija(long id)
    {
        var korisnik = HttpContext.Korisnik();
        var r = baza.Upit("""
            SELECT r.id, r.pacijent, r.napomena, r.kreirano, t.pocetak, l.ime, l.prezime, l.specijalizacija, l.ordinacija,
                   k.ime AS pacijent_ime, k.prezime AS pacijent_prezime
            FROM rezervacije r
            JOIN termini t ON t.id = r.termin_id
            JOIN lijecnici l ON l.id = t.lijecnik_id
            LEFT JOIN korisnici k ON k.username = r.pacijent
            WHERE r.id = $id
            """, ("$id", id)).FirstOrDefault();
        if (r is null || (r.Tekst("pacijent") != korisnik.Username && !korisnik.JeAdmin))
        {
            return NotFound(new { greska = "Rezervacija ne postoji." });
        }

        var pocetak = r.Tekst("pocetak").Replace('T', ' ');
// @@VULN S09
        var tijelo = $"""
            <h1>Potvrda rezervacije br. {r.Broj("id")}</h1>
            <table>
            <tr><th>Pacijent</th><td>{r.Tekst("pacijent_ime")} {r.Tekst("pacijent_prezime")} ({r.Tekst("pacijent")})</td></tr>
            <tr><th>Liječnik</th><td>dr. {r.Tekst("ime")} {r.Tekst("prezime")}, {r.Tekst("specijalizacija")}</td></tr>
            <tr><th>Termin</th><td>{pocetak}, {r.Tekst("ordinacija")}</td></tr>
            <tr><th>Napomena</th><td>{r.Tekst("napomena")}</td></tr>
            <tr><th>Rezervirano</th><td>{r.Tekst("kreirano")}</td></tr>
            </table>
            <p>Molimo dođite 10 minuta prije termina i ponesite zdravstvenu iskaznicu.</p>
            """;
// @@SECURE S09
        var tijelo = $"""
            <h1>Potvrda rezervacije br. {r.Broj("id")}</h1>
            <table>
            <tr><th>Pacijent</th><td>{H(r.Tekst("pacijent_ime"))} {H(r.Tekst("pacijent_prezime"))} ({H(r.Tekst("pacijent"))})</td></tr>
            <tr><th>Liječnik</th><td>dr. {H(r.Tekst("ime"))} {H(r.Tekst("prezime"))}, {H(r.Tekst("specijalizacija"))}</td></tr>
            <tr><th>Termin</th><td>{H(pocetak)}, {H(r.Tekst("ordinacija"))}</td></tr>
            <tr><th>Napomena</th><td>{H(r.Tekst("napomena"))}</td></tr>
            <tr><th>Rezervirano</th><td>{H(r.Tekst("kreirano"))}</td></tr>
            </table>
            <p>Molimo dođite 10 minuta prije termina i ponesite zdravstvenu iskaznicu.</p>
            """;
        Response.Headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'";
// @@END S09
        return HtmlStranica.Odgovor($"Potvrda rezervacije {id}", tijelo);
    }
// @@VULN S09
// @@SECURE S09

    private static string H(string tekst) => HtmlEncoder.Default.Encode(tekst);
// @@END S09
}
