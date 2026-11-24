using System.Net;
using Knjiznica.Tests.Infrastruktura;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>K05 – A02 Security Misconfiguration: detalji greške u odgovoru i nedostatak sigurnosnih zaglavlja (CWE-209, CWE-693).</summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K05")]
public sealed class K05KonfiguracijaTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Fact]
    public async Task NepostojecaKnjigaBezDetaljaGreske()
    {
        var odgovor = await app.CreateClient().GetAsync("/api/knjige/999999");
        var tijelo = await odgovor.Content.ReadAsStringAsync();
        Assert.Equal(HttpStatusCode.NotFound, odgovor.StatusCode);
        Assert.DoesNotContain("Exception", tijelo);
        Assert.DoesNotContain("   at ", tijelo);
        Assert.DoesNotContain("Knjiznica.Api", tijelo);
    }

    [Fact]
    public async Task OdgovoriImajuSigurnosnaZaglavlja()
    {
        var odgovor = await app.CreateClient().GetAsync("/api/knjige");
        Assert.Equal("nosniff", Zaglavlje(odgovor, "X-Content-Type-Options"));
        Assert.Equal("DENY", Zaglavlje(odgovor, "X-Frame-Options"));
        Assert.False(string.IsNullOrEmpty(Zaglavlje(odgovor, "Content-Security-Policy")));
    }

    private static string? Zaglavlje(HttpResponseMessage odgovor, string naziv) =>
        odgovor.Headers.TryGetValues(naziv, out var vrijednosti) ? vrijednosti.FirstOrDefault() : null;
}
