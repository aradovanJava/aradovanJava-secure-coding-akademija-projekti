using System.Net;
using System.Net.Http.Json;
using Knjiznica.Tests.Infrastruktura;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>K08 – A10 Mishandling of Exceptional Conditions: greška u provjeri članarine propušta posudbu (CWE-636, CWE-755).</summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K08")]
public sealed class K08ProvjeraClanarineTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Fact]
    public async Task IsteklaClanarinaNeSmijePosuditi()
    {
        var odgovor = await (await app.KlijentZaAsync("marko")).PostAsJsonAsync("/api/posudbe", new { knjigaId = 4 });
        Assert.Equal(HttpStatusCode.Forbidden, odgovor.StatusCode);
    }

    [Fact]
    public async Task NepoznatStatusClanarineZnaciOdbijanje()
    {
        // Iva ima status SUSPENDIRANA koji provjera ne poznaje: greška u provjeri ne smije značiti "dopušteno".
        var odgovor = await (await app.KlijentZaAsync("iva")).PostAsJsonAsync("/api/posudbe", new { knjigaId = 4 });
        Assert.Equal(HttpStatusCode.Forbidden, odgovor.StatusCode);
    }
}
