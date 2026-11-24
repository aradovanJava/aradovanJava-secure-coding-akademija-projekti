using System.Net;
using System.Net.Http.Json;
using System.Text;
using Knjiznica.Tests.Infrastruktura;
using Xunit;

namespace Knjiznica.Tests.Funkcionalni;

/// <summary>Funkcionalni testovi: aplikacija radi ono što korisnici očekuju (prolaze i prije i nakon ispravaka).</summary>
[Trait("Category", "Funkcionalni")]
public sealed class FunkcionalniTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Fact]
    public async Task PrijavaIspravnimPodacima()
    {
        var odgovor = await app.CreateClient().PostAsJsonAsync("/api/prijava", new { korisnickoIme = "ana", lozinka = "Ana123!" });
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        var json = await odgovor.CitajJsonAsync();
        Assert.Equal("CLAN", json.GetProperty("uloga").GetString());
        Assert.True(json.GetProperty("token").GetString()!.Length >= 32);
    }

    [Fact]
    public async Task PrijavaKrivomLozinkomVraca401()
    {
        var odgovor = await app.CreateClient().PostAsJsonAsync("/api/prijava", new { korisnickoIme = "ana", lozinka = "kriva-lozinka" });
        Assert.Equal(HttpStatusCode.Unauthorized, odgovor.StatusCode);
    }

    [Fact]
    public async Task RegistracijaIPrijavaNovogClana()
    {
        var klijent = app.CreateClient();
        var podaci = new { korisnickoIme = "novi.clan", lozinka = "NovaLozinka1!", ime = "Novi Član", email = "n@primjer.hr" };
        Assert.Equal(HttpStatusCode.Created, (await klijent.PostAsJsonAsync("/api/registracija", podaci)).StatusCode);
        Assert.Equal(HttpStatusCode.Conflict, (await klijent.PostAsJsonAsync("/api/registracija", podaci)).StatusCode);
        var prijava = await klijent.PostAsJsonAsync("/api/prijava", new { korisnickoIme = "novi.clan", lozinka = "NovaLozinka1!" });
        Assert.Equal(HttpStatusCode.OK, prijava.StatusCode);
    }

    [Fact]
    public async Task PretragaKataloga()
    {
        var odgovor = await app.CreateClient().GetAsync("/api/knjige?trazi=Proces");
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal(new[] { "Proces" }, Naslovi(await odgovor.CitajJsonAsync()));
    }

    [Fact]
    public async Task PretragaBezUpitaVracaSamoJavneKnjige()
    {
        var naslovi = Naslovi(await (await app.CreateClient().GetAsync("/api/knjige")).CitajJsonAsync());
        Assert.Contains("Zlatarovo zlato", naslovi);
        Assert.DoesNotContain("Interni popis za otpis", naslovi);
    }

    [Fact]
    public async Task PodaciOKnjizi()
    {
        var odgovor = await app.CreateClient().GetAsync("/api/knjige/2");
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal("Ivo Andrić", (await odgovor.CitajJsonAsync()).GetProperty("autor").GetString());
    }

    [Fact]
    public async Task ClanVidiSvojProfil()
    {
        var odgovor = await (await app.KlijentZaAsync("ana")).GetAsync("/api/clanovi/1");
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal("ana", (await odgovor.CitajJsonAsync()).GetProperty("korisnickoIme").GetString());
    }

    [Fact]
    public async Task KnjiznicarVidiProfilClana()
    {
        var odgovor = await (await app.KlijentZaAsync("knjiznicar")).GetAsync("/api/clanovi/2");
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal("marko", (await odgovor.CitajJsonAsync()).GetProperty("korisnickoIme").GetString());
    }

    [Fact]
    public async Task ProfilBezPrijaveVraca401()
    {
        Assert.Equal(HttpStatusCode.Unauthorized, (await app.CreateClient().GetAsync("/api/clanovi/1")).StatusCode);
    }

    [Fact]
    public async Task KnjiznicarUvoziKatalog()
    {
        const string katalog = "- naslov: Kiklop\n  autor: Ranko Marinković\n  godina: 1965\n" +
                               "- naslov: Gospoda Glembajevi\n  autor: Miroslav Krleža\n  godina: 1929\n";
        var klijent = await app.KlijentZaAsync("knjiznicar");
        var odgovor = await klijent.PostAsync("/api/katalog/uvoz", new StringContent(katalog, Encoding.UTF8, "application/yaml"));
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal(2, (await odgovor.CitajJsonAsync()).GetProperty("uvezeno").GetInt32());
        Assert.Equal(new[] { "Kiklop" }, Naslovi(await (await klijent.GetAsync("/api/knjige?trazi=Kiklop")).CitajJsonAsync()));
    }

    [Fact]
    public async Task ClanNeMozeUvozitiKatalog()
    {
        var odgovor = await (await app.KlijentZaAsync("ana")).PostAsync("/api/katalog/uvoz",
            new StringContent("- naslov: X\n  autor: Y\n  godina: 2000\n", Encoding.UTF8, "application/yaml"));
        Assert.Equal(HttpStatusCode.Forbidden, odgovor.StatusCode);
    }

    [Fact]
    public async Task ClanSAktivnomClanarinomPosudjuje()
    {
        var odgovor = await (await app.KlijentZaAsync("ana")).PostAsJsonAsync("/api/posudbe", new { knjigaId = 5 });
        Assert.Equal(HttpStatusCode.Created, odgovor.StatusCode);
        Assert.Equal(5, (await odgovor.CitajJsonAsync()).GetProperty("knjigaId").GetInt64());
    }

    [Fact]
    public async Task ProduljenjePosudbeZaSedamDana()
    {
        var odgovor = await (await app.KlijentZaAsync("ana")).PostAsJsonAsync("/api/posudbe/1/produzi", new { dana = 7 });
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal("2026-12-17", (await odgovor.CitajJsonAsync()).GetProperty("rok").GetString());
    }

    [Fact]
    public async Task PopisVlastitihPosudbi()
    {
        var json = await (await (await app.KlijentZaAsync("ana")).GetAsync("/api/posudbe")).CitajJsonAsync();
        var knjige = json.EnumerateArray().Select(p => p.GetProperty("knjigaId").GetInt64()).ToList();
        Assert.Contains(1L, knjige);
        Assert.Contains(2L, knjige);
        Assert.Contains(3L, knjige);
    }

    private static List<string> Naslovi(System.Text.Json.JsonElement json) =>
        json.EnumerateArray().Select(k => k.GetProperty("naslov").GetString()!).ToList();
}
