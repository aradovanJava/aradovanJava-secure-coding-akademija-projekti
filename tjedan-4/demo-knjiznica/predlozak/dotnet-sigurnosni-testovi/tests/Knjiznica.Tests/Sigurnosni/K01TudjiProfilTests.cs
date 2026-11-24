using System.Net;
using Knjiznica.Tests.Infrastruktura;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>K01 – A01 Broken Access Control: pristup tuđem profilu promjenom ID-a (IDOR, CWE-639).</summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K01")]
public sealed class K01TudjiProfilTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Fact]
    public async Task ClanNeVidiTudjiProfil()
    {
        // Ana (id 1) traži Markov profil (id 2): mora dobiti 404 i nijedan Markov podatak.
        var odgovor = await (await app.KlijentZaAsync("ana")).GetAsync("/api/clanovi/2");
        var tijelo = await odgovor.Content.ReadAsStringAsync();
        Assert.Equal(HttpStatusCode.NotFound, odgovor.StatusCode);
        Assert.DoesNotContain("marko", tijelo, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("Vukovarska", tijelo);
    }

    [Fact]
    public async Task OdgovorNeOtkrivaPostojiLiClan()
    {
        var ana = await app.KlijentZaAsync("ana");
        var tudji = await ana.GetAsync("/api/clanovi/2");
        var nepostojeci = await ana.GetAsync("/api/clanovi/999");
        Assert.Equal(nepostojeci.StatusCode, tudji.StatusCode);
        Assert.Equal(await nepostojeci.Content.ReadAsStringAsync(), await tudji.Content.ReadAsStringAsync());
    }
}
