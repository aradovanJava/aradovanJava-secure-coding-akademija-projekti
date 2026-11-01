using System.Net;
using System.Net.Http.Json;
using MedTermin.Tests.Infrastruktura;
using Xunit;

namespace MedTermin.Tests.Funkcionalno;

[Trait("Category", "Funkcionalno")]
public sealed class RezervacijeTests(MedTerminFactory factory) : IClassFixture<MedTerminFactory>
{
    private static async Task<long> RezervirajAsync(HttpClient klijent, long terminId, string napomena)
    {
        var odgovor = await klijent.PostAsJsonAsync("/api/rezervacije", new { terminId, napomena, oib = "48291736504" });
        Assert.Equal(HttpStatusCode.Created, odgovor.StatusCode);
        return (await odgovor.CitajJsonAsync()).GetProperty("id").GetInt64();
    }

    [Fact]
    public async Task MojeRezervacijeSadrzePocetnuRezervaciju()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var moje = await (await klijent.GetAsync("/api/rezervacije/moje")).CitajJsonAsync();

        var prva = moje.EnumerateArray().Single(r => r.GetProperty("id").GetInt64() == 1);
        Assert.Equal("Kontrolni pregled tlaka", prva.GetProperty("napomena").GetString());
        Assert.Equal("*******6504", prva.GetProperty("oib").GetString());
        Assert.DoesNotContain(moje.EnumerateArray(), r => r.GetProperty("id").GetInt64() == 2);
    }

    [Fact]
    public async Task NovaRezervacijaVidljivaJeUMojimRezervacijama()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var id = await RezervirajAsync(klijent, 3, "Pregled madeža");

        var moje = await (await klijent.GetAsync("/api/rezervacije/moje")).CitajJsonAsync();
        var nova = moje.EnumerateArray().Single(r => r.GetProperty("id").GetInt64() == id);
        Assert.Equal(3, nova.GetProperty("terminId").GetInt64());
        Assert.Equal("Pregled madeža", nova.GetProperty("napomena").GetString());

        var termini = await (await klijent.GetAsync("/api/termini?lijecnikId=2")).CitajJsonAsync();
        var termin = termini.EnumerateArray().Single(t => t.GetProperty("id").GetInt64() == 3);
        Assert.Equal(0, termin.GetProperty("slobodno").GetInt32());
    }

    [Fact]
    public async Task PopunjenTerminVraca409()
    {
        var klijent = await factory.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await klijent.PostAsJsonAsync("/api/rezervacije", new { terminId = 1, napomena = "Kontrola", oib = "73019485267" });

        Assert.Equal(HttpStatusCode.Conflict, odgovor.StatusCode);
    }

    [Fact]
    public async Task NeispravanOibVraca400()
    {
        var klijent = await factory.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await klijent.PostAsJsonAsync("/api/rezervacije", new { terminId = 5, napomena = "Kontrola", oib = "123" });

        Assert.Equal(HttpStatusCode.BadRequest, odgovor.StatusCode);
    }

    [Fact]
    public async Task VlastitaRezervacijaSeMozeOtkazati()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");
        var id = await RezervirajAsync(klijent, 4, "Kontrola nakon terapije");

        var brisanje = await klijent.DeleteAsync($"/api/rezervacije/{id}");

        Assert.Equal(HttpStatusCode.NoContent, brisanje.StatusCode);
        var moje = await (await klijent.GetAsync("/api/rezervacije/moje")).CitajJsonAsync();
        Assert.DoesNotContain(moje.EnumerateArray(), r => r.GetProperty("id").GetInt64() == id);
    }

    [Fact]
    public async Task IspisPotvrdeSadrziNapomenu()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");
        var id = await RezervirajAsync(klijent, 9, "Molim jutarnji dolazak, hvala");

        var odgovor = await klijent.GetAsync($"/ispis/rezervacije/{id}");

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal("text/html", odgovor.Content.Headers.ContentType?.MediaType);
        var html = await odgovor.Content.ReadAsStringAsync();
        Assert.Contains("Molim jutarnji dolazak, hvala", html);
        Assert.Contains("Potvrda rezervacije", html);
    }
}
