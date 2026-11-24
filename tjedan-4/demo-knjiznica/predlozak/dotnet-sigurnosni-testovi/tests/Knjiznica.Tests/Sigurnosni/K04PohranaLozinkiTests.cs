using System.Net;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Knjiznica.Api.Infrastruktura;
using Knjiznica.Tests.Infrastruktura;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>K04 – A04 Cryptographic Failures: lozinke spremljene kao MD5 bez soli (CWE-916, CWE-327).</summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K04")]
public sealed class K04PohranaLozinkiTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    private const string Lozinka = "IstaLozinka123!";

    [Fact]
    public async Task IstaLozinkaDajeRazliciteHasheve()
    {
        await Registriraj("k04.prvi");
        await Registriraj("k04.drugi");
        Assert.NotEqual(Hash("k04.prvi"), Hash("k04.drugi"));
    }

    [Fact]
    public async Task HashNijeMd5()
    {
        await Registriraj("k04.treci");
        var md5 = Convert.ToHexString(MD5.HashData(Encoding.UTF8.GetBytes(Lozinka))).ToLowerInvariant();
        var pohranjeno = Hash("k04.treci");
        Assert.NotEqual(md5, pohranjeno);
        Assert.DoesNotMatch("^[0-9a-f]{32}$", pohranjeno);
    }

    private async Task Registriraj(string ime)
    {
        var odgovor = await app.CreateClient().PostAsJsonAsync("/api/registracija",
            new { korisnickoIme = ime, lozinka = Lozinka, ime = "Test", email = $"{ime}@primjer.hr" });
        Assert.Equal(HttpStatusCode.Created, odgovor.StatusCode);
    }

    private string Hash(string ime) =>
        (string)app.Services.GetRequiredService<Baza>()
            .Jedan("SELECT lozinka_hash FROM korisnici WHERE korisnicko_ime = $ime", ("$ime", ime))!["lozinka_hash"]!;
}
