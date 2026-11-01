using System.Text;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

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
            <!DOCTYPE dogadjaji [<!ENTITY e SYSTEM "{uri}">]>
            <dogadjaji><dogadjaj><naziv>&e;</naziv><mjesto>Lisinski, Zagreb</mjesto><datum>2026-12-12T20:00</datum><cijena>25.00</cijena><kapacitet>300</kapacitet></dogadjaj></dogadjaji>
            """;
        var organizator = await app.KlijentZaAsync("organizator", "Ovlasteni12345!");

        var odgovor = await organizator.PostAsync("/api/dogadjaji/uvoz", new StringContent(xml, Encoding.UTF8, "application/xml"));
        var tijelo = await odgovor.Content.ReadAsStringAsync();

        Assert.DoesNotContain(tajna, tijelo);
    }
}
