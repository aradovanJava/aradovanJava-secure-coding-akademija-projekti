using System.Text;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S05 – XXE: vanjski entiteti u XML-u ne smiju se razrješavati.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S05")]
public sealed class S05UvozXmlaTests
{
    [Fact]
    public async Task VanjskiEntitetNeSmijeProcitatiDatoteku()
    {
        await using var app = new SkrivenoApp();
        var kanarinac = Path.Combine(app.Mapa, $"kanarinac-{Guid.NewGuid():N}.txt");
        var tajna = $"KANARINAC{Guid.NewGuid():N}";
        File.WriteAllText(kanarinac, tajna);
        var uri = new Uri(kanarinac).AbsoluteUri;
        var xml = $"""
            <?xml version="1.0" encoding="utf-8"?>
            <!DOCTYPE termini [<!ENTITY e SYSTEM "{uri}">]>
            <termini><termin><lijecnikId>1</lijecnikId><pocetak>2026-12-01T09:00</pocetak><kapacitet>1</kapacitet><napomena>&e;</napomena></termin></termini>
            """;
        var lijecnik = await app.KlijentZaAsync("dr.horvat", "Ovlasteni12345!");

        var odgovor = await lijecnik.PostAsync("/api/termini/uvoz", new StringContent(xml, Encoding.UTF8, "application/xml"));
        var tijelo = await odgovor.Content.ReadAsStringAsync();

        Assert.DoesNotContain(tajna, tijelo);
    }
}
