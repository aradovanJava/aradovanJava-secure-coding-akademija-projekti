using System.Net;
using System.Text.Json;
using MedTermin.Tests.Infrastruktura;
using Xunit;

namespace MedTermin.Tests.Funkcionalno;

[Trait("Category", "Funkcionalno")]
public sealed class LijecniciITerminiTests(MedTerminFactory factory) : IClassFixture<MedTerminFactory>
{
    private static List<string> Prezimena(JsonElement json) =>
        json.EnumerateArray().Select(l => l.GetProperty("prezime").GetString()!).ToList();

    [Fact]
    public async Task ZadanoSortiranjePoPrezimenuUzlazno()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await klijent.GetAsync("/api/lijecnici");

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        var prezimena = Prezimena(await odgovor.CitajJsonAsync());
        Assert.Equal(6, prezimena.Count);
        Assert.Equal("Babić", prezimena[0]);
        Assert.Equal("Perić", prezimena[^1]);
    }

    [Fact]
    public async Task SortiranjePoPrezimenuSilazno()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var prezimena = Prezimena(await (await klijent.GetAsync("/api/lijecnici?sort=prezime&smjer=desc")).CitajJsonAsync());

        Assert.Equal(new[] { "Perić", "Novak", "Kovačević", "Jurić", "Horvat", "Babić" }, prezimena);
    }

    [Fact]
    public async Task SortiranjePoImenuISpecijalizaciji()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var poImenu = await (await klijent.GetAsync("/api/lijecnici?sort=ime&smjer=asc")).CitajJsonAsync();
        var poSpecijalizaciji = await (await klijent.GetAsync("/api/lijecnici?sort=specijalizacija&smjer=asc")).CitajJsonAsync();

        Assert.Equal("Damir", poImenu[0].GetProperty("ime").GetString());
        Assert.Equal("Tomislav", poImenu[5].GetProperty("ime").GetString());
        Assert.Equal("Dermatologija", poSpecijalizaciji[0].GetProperty("specijalizacija").GetString());
    }

    [Fact]
    public async Task TerminiLijecnikaPrikazujuSlobodnaMjesta()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var termini = await (await klijent.GetAsync("/api/termini?lijecnikId=1")).CitajJsonAsync();

        Assert.True(termini.GetArrayLength() >= 3);
        var prvi = termini.EnumerateArray().Single(t => t.GetProperty("id").GetInt64() == 1);
        Assert.Equal(0, prvi.GetProperty("slobodno").GetInt32());
        var grupni = termini.EnumerateArray().Single(t => t.GetProperty("id").GetInt64() == 9);
        Assert.Equal(3, grupni.GetProperty("kapacitet").GetInt32());
    }

    [Fact]
    public async Task PopisLijecnikaZahtijevaPrijavu()
    {
        var odgovor = await factory.CreateClient().GetAsync("/api/lijecnici");

        Assert.Equal(HttpStatusCode.Unauthorized, odgovor.StatusCode);
    }
}
