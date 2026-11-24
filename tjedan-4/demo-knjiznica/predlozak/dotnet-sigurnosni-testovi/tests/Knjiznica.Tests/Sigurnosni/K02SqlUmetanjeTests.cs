using System.Net;
using Knjiznica.Tests.Infrastruktura;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>K02 – A05 Injection: SQL umetanje u pretrazi kataloga (CWE-89).</summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K02")]
public sealed class K02SqlUmetanjeTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Theory]
    [InlineData("' OR '1'='1' --")]
    [InlineData("%' OR 1=1 --")]
    public async Task UvjetUvijekIstinitNeOtkrivaSkriveneKnjige(string upit)
    {
        var odgovor = await app.CreateClient().GetAsync("/api/knjige?trazi=" + Uri.EscapeDataString(upit));
        Assert.Contains(odgovor.StatusCode, new[] { HttpStatusCode.OK, HttpStatusCode.BadRequest });
        Assert.DoesNotContain("Interni popis za otpis", await odgovor.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task UnionNeVracaKorisnickeRacune()
    {
        const string upit = "%' UNION SELECT id, korisnicko_ime, lozinka_hash, 0 FROM korisnici --";
        var odgovor = await app.CreateClient().GetAsync("/api/knjige?trazi=" + Uri.EscapeDataString(upit));
        var tijelo = await odgovor.Content.ReadAsStringAsync();
        Assert.Contains(odgovor.StatusCode, new[] { HttpStatusCode.OK, HttpStatusCode.BadRequest });
        Assert.DoesNotContain("knjiznicar", tijelo);
        Assert.DoesNotContain("marko", tijelo);
    }
}
