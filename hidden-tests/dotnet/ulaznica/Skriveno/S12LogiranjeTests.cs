using System.Net;
using System.Net.Http.Json;
using Microsoft.Extensions.Logging;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

/// <summary>S12 – u logu nema lozinke ni punog OIB-a, a neuspjela prijava se bilježi.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S12")]
public sealed class S12LogiranjeTests
{
    [Fact]
    public async Task LozinkaSeNeZapisujeULog()
    {
        await using var app = new SkrivenoApp();

        var prijava = await app.Klijent().PostAsJsonAsync("/api/auth/login", new { username = "ana", password = "Ana12345!" });

        Assert.Equal(HttpStatusCode.OK, prijava.StatusCode);
        Assert.DoesNotContain(app.Log.Zapisi, z => z.Poruka.Contains("Ana12345!", StringComparison.Ordinal));
    }

    [Fact]
    public async Task OibSeNeZapisujeUCijelosti()
    {
        await using var app = new SkrivenoApp();
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await ana.PostAsJsonAsync("/api/narudzbe", new { dogadjajId = 3, kolicina = 1, imeNaUlaznici = "Ana Anić", oib = "48291736504" });

        Assert.Equal(HttpStatusCode.Created, odgovor.StatusCode);
        Assert.DoesNotContain(app.Log.Zapisi, z => z.Poruka.Contains("48291736504", StringComparison.Ordinal));
    }

    [Fact]
    public async Task NeuspjelaPrijavaSeBiljeziUpozorenjem()
    {
        await using var app = new SkrivenoApp();

        var prijava = await app.Klijent().PostAsJsonAsync("/api/auth/login", new { username = "marko", password = "pogresna" });

        Assert.Equal(HttpStatusCode.Unauthorized, prijava.StatusCode);
        Assert.Contains(app.Log.Zapisi, z => z.Razina >= LogLevel.Warning && z.Poruka.Contains("marko", StringComparison.Ordinal));
        Assert.DoesNotContain(app.Log.Zapisi, z => z.Poruka.Contains("pogresna", StringComparison.Ordinal));
    }
}
