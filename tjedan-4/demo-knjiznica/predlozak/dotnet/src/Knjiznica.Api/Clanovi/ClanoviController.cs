using Knjiznica.Api.Autentikacija;
using Knjiznica.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace Knjiznica.Api.Clanovi;

/// <summary>Profil člana knjižnice.</summary>
[ApiController]
public sealed class ClanoviController(Baza baza) : ControllerBase
{
    [HttpGet("/api/clanovi/{id:long}")]
    public IActionResult Profil(long id)
    {
        var korisnik = HttpContext.Korisnik();
        if (korisnik is null)
        {
            return Greska.Neprijavljen();
        }
        // @@VULN K01
        // @@SECURE K01
        // Član vidi samo svoj profil; knjižničar vidi sve. Tuđi profil = 404 (ne otkrivamo postoji li).
        if (id != korisnik.Id && !korisnik.JeKnjiznicar)
        {
            return Greska.NijePronadjeno("Član nije pronađen.");
        }
        // @@END K01
        var red = baza.Jedan(
            "SELECT id, korisnicko_ime, ime, email, adresa, telefon FROM korisnici WHERE id = $id", ("$id", id));
        if (red is null)
        {
            return Greska.NijePronadjeno("Član nije pronađen.");
        }
        return Ok(new
        {
            id = red["id"],
            korisnickoIme = red["korisnicko_ime"],
            ime = red["ime"],
            email = red["email"],
            adresa = red["adresa"],
            telefon = red["telefon"],
        });
    }
}
