using System.Net.Http.Json;
using Knjiznica.Tests.Infrastruktura;
using Microsoft.Extensions.Logging;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>
/// K07 – A09 Security Logging and Alerting Failures: lozinka u dnevniku, nema sigurnosnih događaja,
/// krivotvorenje zapisa (CWE-532, CWE-778, CWE-117).
/// </summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K07")]
public sealed class K07ZapisiTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Fact]
    public async Task LozinkaSeNeZapisuje()
    {
        var klijent = app.CreateClient();
        await klijent.PostAsJsonAsync("/api/prijava", new { korisnickoIme = "ana", lozinka = "Ana123!" });
        await klijent.PostAsJsonAsync("/api/prijava", new { korisnickoIme = "ana", lozinka = "TajnaKojuNitkoNeSmijeVidjeti" });
        Assert.DoesNotContain(app.Zapisi, z => z.Poruka.Contains("Ana123!") || z.Poruka.Contains("TajnaKojuNitkoNeSmijeVidjeti"));
    }

    [Fact]
    public async Task NeuspjelaPrijavaJeSigurnosniDogadjaj()
    {
        await app.CreateClient().PostAsJsonAsync("/api/prijava", new { korisnickoIme = "marko", lozinka = "pogresna" });
        Assert.Contains(app.Zapisi, z => z.Razina >= LogLevel.Warning
                                         && z.Poruka.Contains("SECURITY_EVENT") && z.Poruka.Contains("LOGIN_FAILED"));
    }

    [Fact]
    public async Task NoviRedUImenuNeKrivotvoriZapis()
    {
        const string ime = "ana\n2026-11-25 10:00:00 INFO SECURITY_EVENT LOGIN_SUCCESS korisnik=knjiznicar";
        await app.CreateClient().PostAsJsonAsync("/api/prijava", new { korisnickoIme = ime, lozinka = "x" });
        Assert.DoesNotContain(app.Zapisi, z => z.Poruka.Contains('\n'));
    }
}
