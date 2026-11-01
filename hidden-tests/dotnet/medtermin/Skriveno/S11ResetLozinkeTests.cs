using System.Globalization;
using System.Net;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S11 – token za obnovu lozinke mora biti nepredvidljiv i jednokratan.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S11")]
public sealed class S11ResetLozinkeTests
{
    [Fact]
    public async Task PredvidljivTokenNeVrijedi()
    {
        await using var app = new SkrivenoApp();
        var klijent = app.Klijent();
        var zahtjev = await klijent.PostAsJsonAsync("/api/auth/reset-zahtjev", new { username = "ana" });
        Assert.Equal(HttpStatusCode.Accepted, zahtjev.StatusCode);

        var datumi = new[] { DateTime.Now, DateTime.UtcNow, DateTime.Now.AddDays(-1) }
            .Select(d => d.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture))
            .Distinct();
        foreach (var datum in datumi)
        {
            var pogodeni = Convert.ToHexString(MD5.HashData(Encoding.UTF8.GetBytes("ana" + datum))).ToLowerInvariant();
            foreach (var token in new[] { pogodeni, pogodeni.ToUpperInvariant() })
            {
                var reset = await klijent.PostAsJsonAsync("/api/auth/reset", new { token, novaLozinka = "Preuzeto12345!" });
                Assert.Equal(HttpStatusCode.BadRequest, reset.StatusCode);
            }
        }

        var prijava = await klijent.PostAsJsonAsync("/api/auth/login", new { username = "ana", password = "Ana12345!" });
        Assert.Equal(HttpStatusCode.OK, prijava.StatusCode);
    }

    [Fact]
    public async Task TokenIzPorukeVrijediSamoJednom()
    {
        await using var app = new SkrivenoApp();
        var klijent = app.Klijent();
        var zahtjev = await klijent.PostAsJsonAsync("/api/auth/reset-zahtjev", new { username = "ana" });
        Assert.Equal(HttpStatusCode.Accepted, zahtjev.StatusCode);

        var poruka = Directory.GetFiles(app.DirektorijPoste, "ana-*.txt").OrderBy(f => f, StringComparer.Ordinal).Last();
        var token = Regex.Match(File.ReadAllText(poruka), @"Token: (\S+)").Groups[1].Value;
        Assert.False(string.IsNullOrEmpty(token), "U poruci nema tokena.");

        var prvi = await klijent.PostAsJsonAsync("/api/auth/reset", new { token, novaLozinka = "PrvaNova12345!" });
        var drugi = await klijent.PostAsJsonAsync("/api/auth/reset", new { token, novaLozinka = "DrugaNova12345!" });

        Assert.Equal(HttpStatusCode.OK, prvi.StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, drugi.StatusCode);
        var prijava = await klijent.PostAsJsonAsync("/api/auth/login", new { username = "ana", password = "PrvaNova12345!" });
        Assert.Equal(HttpStatusCode.OK, prijava.StatusCode);
    }
}
