using System.Globalization;
using System.Text;
using System.Xml;
using System.Xml.Linq;
using MedTermin.Api.Autentikacija;
using MedTermin.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace MedTermin.Api.Poliklinika;

/// <summary>Termini pregleda i uvoz rasporeda iz XML-a.</summary>
[ApiController]
[Route("api/termini")]
[PotrebnaPrijava]
public sealed class TerminiController(Baza baza, ILogger<TerminiController> logger) : ControllerBase
{
    private const int NajvecaVelicinaXml = 100_000;
    private const string FormatPocetka = "yyyy-MM-dd'T'HH:mm";

    private sealed record NoviTermin(long LijecnikId, string Pocetak, int Kapacitet, string Napomena);

    /// <summary><c>GET /api/termini?lijecnikId=1</c></summary>
    [HttpGet]
    public IActionResult Popis([FromQuery] long? lijecnikId)
    {
        var redci = baza.Upit("""
            SELECT t.id, t.lijecnik_id, l.ime, l.prezime, t.pocetak, t.kapacitet, t.zauzeto, t.napomena
            FROM termini t JOIN lijecnici l ON l.id = t.lijecnik_id
            WHERE $lijecnik IS NULL OR t.lijecnik_id = $lijecnik
            ORDER BY t.pocetak, t.id
            """, ("$lijecnik", lijecnikId));
        return Ok(redci.Select(r => new
        {
            id = r.Broj("id"),
            lijecnikId = r.Broj("lijecnik_id"),
            lijecnik = $"dr. {r.Tekst("ime")} {r.Tekst("prezime")}",
            pocetak = r.Tekst("pocetak"),
            kapacitet = r.Broj("kapacitet"),
            zauzeto = r.Broj("zauzeto"),
            slobodno = Math.Max(0, r.Broj("kapacitet") - r.Broj("zauzeto")),
            napomena = r.Tekst("napomena"),
        }));
    }

    /// <summary>
    /// Uvoz rasporeda: <c>&lt;termini&gt;&lt;termin&gt;&lt;lijecnikId&gt;1&lt;/lijecnikId&gt;&lt;pocetak&gt;2026-12-01T09:00&lt;/pocetak&gt;
    /// &lt;kapacitet&gt;1&lt;/kapacitet&gt;&lt;napomena&gt;…&lt;/napomena&gt;&lt;/termin&gt;&lt;/termini&gt;</c>
    /// </summary>
    [HttpPost("uvoz")]
    [PotrebnaPrijava(Aplikacija.PovlastenaUloga, Uloge.Admin)]
    public async Task<IActionResult> Uvoz()
    {
        string xml;
        using (var citac = new StreamReader(Request.Body, Encoding.UTF8))
        {
            xml = await citac.ReadToEndAsync(HttpContext.RequestAborted);
        }
        if (xml.Length > NajvecaVelicinaXml)
        {
            return BadRequest(new { greska = "Datoteka je prevelika." });
        }

        List<NoviTermin> termini;
        try
        {
            termini = ProcitajXml(xml);
        }
        catch (Exception ex) when (ex is XmlException or FormatException or OverflowException)
        {
            logger.LogInformation("Uvoz termina nije uspio: {Poruka}", ex.Message);
            return BadRequest(new { greska = "Neispravan XML." });
        }

        var lijecnici = baza.Upit("SELECT id FROM lijecnici").Select(r => r.Broj("id")).ToHashSet();
        var nepoznat = termini.FirstOrDefault(t => !lijecnici.Contains(t.LijecnikId));
        if (nepoznat is not null)
        {
            return BadRequest(new { greska = $"Liječnik s ID-om {nepoznat.LijecnikId} ne postoji." });
        }

        var uvezeni = new List<object>();
        using (var veza = baza.Otvori())
        using (var transakcija = veza.BeginTransaction())
        {
            foreach (var termin in termini)
            {
                var id = Baza.Umetni(veza, transakcija,
                    "INSERT INTO termini (lijecnik_id, pocetak, kapacitet, zauzeto, napomena) VALUES ($l, $p, $k, 0, $n)",
                    ("$l", termin.LijecnikId), ("$p", termin.Pocetak), ("$k", termin.Kapacitet), ("$n", termin.Napomena));
                uvezeni.Add(new { id, pocetak = termin.Pocetak, napomena = termin.Napomena });
            }
            transakcija.Commit();
        }

        logger.LogInformation("Korisnik {Username} je uvezao {Broj} termina", HttpContext.Korisnik().Username, uvezeni.Count);
        return Ok(new { uvezeno = uvezeni.Count, termini = uvezeni });
    }

    private static List<NoviTermin> ProcitajXml(string xml)
    {
        var postavke = new XmlReaderSettings
        {
// @@VULN S05
            DtdProcessing = DtdProcessing.Parse,
            XmlResolver = new XmlUrlResolver(),
// @@SECURE S05
            DtdProcessing = DtdProcessing.Prohibit,
            XmlResolver = null,
// @@END S05
            IgnoreComments = true,
            IgnoreWhitespace = true,
        };
        using var citac = XmlReader.Create(new StringReader(xml), postavke);
        var dokument = XDocument.Load(citac);
        if (dokument.Root is not { Name.LocalName: "termini" } korijen)
        {
            throw new FormatException("Očekivan je korijenski element <termini>.");
        }

        var termini = new List<NoviTermin>();
        foreach (var element in korijen.Elements("termin"))
        {
            var lijecnikId = long.Parse(Obavezno(element, "lijecnikId"), NumberStyles.Integer, CultureInfo.InvariantCulture);
            var pocetak = DateTime.ParseExact(Obavezno(element, "pocetak"), FormatPocetka, CultureInfo.InvariantCulture);
            var kapacitet = int.Parse(Obavezno(element, "kapacitet"), NumberStyles.Integer, CultureInfo.InvariantCulture);
            if (kapacitet is < 1 or > 100)
            {
                throw new FormatException("Kapacitet mora biti između 1 i 100.");
            }
            var napomena = ((string?)element.Element("napomena") ?? string.Empty).Trim();
            termini.Add(new NoviTermin(lijecnikId, pocetak.ToString(FormatPocetka, CultureInfo.InvariantCulture), kapacitet, napomena));
        }
        if (termini.Count == 0)
        {
            throw new FormatException("XML ne sadrži nijedan termin.");
        }
        return termini;
    }

    private static string Obavezno(XElement element, string naziv) =>
        ((string?)element.Element(naziv))?.Trim() ?? throw new FormatException($"Nedostaje element <{naziv}>.");
}
