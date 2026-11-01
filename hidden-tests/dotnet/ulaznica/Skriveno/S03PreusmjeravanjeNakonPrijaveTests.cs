using System.Net;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

/// <summary>S03 – open redirect nakon web prijave.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S03")]
public sealed class S03PreusmjeravanjeNakonPrijaveTests
{
    [Theory]
    [InlineData("https://zlo.example/x")]
    [InlineData("//zlo.example")]
    [InlineData("/\\zlo.example")]
    public async Task VanjskiReturnUrlSeNePrihvaca(string returnUrl)
    {
        await using var app = new SkrivenoApp();

        var odgovor = await app.Klijent().PostAsync("/prijava", new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["username"] = "ana",
            ["password"] = "Ana12345!",
            ["returnUrl"] = returnUrl,
        }));

        Assert.Equal(HttpStatusCode.Found, odgovor.StatusCode);
        var lokacija = odgovor.Headers.NonValidated.TryGetValues("Location", out var vrijednosti) ? vrijednosti.ToString() : string.Empty;
        Assert.DoesNotContain("zlo.example", lokacija, StringComparison.OrdinalIgnoreCase);
        Assert.StartsWith("/", lokacija);
        Assert.False(lokacija.StartsWith("//", StringComparison.Ordinal) || lokacija.StartsWith("/\\", StringComparison.Ordinal),
            $"Preusmjeravanje mora biti lokalno, a ne '{lokacija}'.");
    }
}
