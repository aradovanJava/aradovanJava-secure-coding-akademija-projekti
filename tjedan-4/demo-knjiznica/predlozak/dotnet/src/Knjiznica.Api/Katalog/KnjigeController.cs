using Knjiznica.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace Knjiznica.Api.Katalog;

/// <summary>Pretraga kataloga i podaci o knjizi (javno, bez prijave).</summary>
[ApiController]
public sealed class KnjigeController(Baza baza) : ControllerBase
{
    [HttpGet("/api/knjige")]
    public IActionResult Pretrazi([FromQuery] string? trazi)
    {
        trazi ??= string.Empty;
        // @@VULN K02
        var sql = "SELECT id, naslov, autor, godina FROM knjige " +
                  "WHERE skrivena = 0 AND naslov LIKE '%" + trazi + "%' ORDER BY naslov";
        return Ok(baza.Upit(sql).Select(Knjiga));
        // @@SECURE K02
        if (trazi.Length > 100)
        {
            return Greska.Neispravno("Upit je predugačak.");
        }
        // parametrizirani upit; znakovi %, _ i \ u upitu traže se doslovno
        var uzorak = "%" + trazi.Replace("\\", "\\\\").Replace("%", "\\%").Replace("_", "\\_") + "%";
        return Ok(baza.Upit(
            "SELECT id, naslov, autor, godina FROM knjige " +
            "WHERE skrivena = 0 AND naslov LIKE $uzorak ESCAPE '\\' ORDER BY naslov",
            ("$uzorak", uzorak)).Select(Knjiga));
        // @@END K02
    }

    [HttpGet("/api/knjige/{id:long}")]
    public IActionResult Dohvati(long id)
    {
        var red = baza.Jedan(
            "SELECT id, naslov, autor, godina FROM knjige WHERE id = $id AND skrivena = 0", ("$id", id));
        // @@VULN K05
        return Ok(Knjiga(red!));
        // @@SECURE K05
        return red is null ? Greska.NijePronadjeno("Knjiga nije pronađena.") : Ok(Knjiga(red));
        // @@END K05
    }

    private static object Knjiga(Dictionary<string, object?> red) =>
        new { id = red["id"], naslov = red["naslov"], autor = red["autor"], godina = red["godina"] };
}
