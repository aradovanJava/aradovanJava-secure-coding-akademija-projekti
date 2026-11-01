using System.Net;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

/// <summary>S08 – SQL injection u parametrima sortiranja.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S08")]
public sealed class S08SortiranjeTests
{
    [Theory]
    [InlineData("(CASE WHEN (SELECT COUNT(*) FROM korisnici)>0 THEN naziv ELSE mjesto END)", "asc")]
    [InlineData("datum;--", "asc")]
    [InlineData("datum", "asc,(SELECT 1)")]
    public async Task NeispravanParametarSortiranjaVraca400(string sort, string smjer)
    {
        await using var app = new SkrivenoApp();
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await ana.GetAsync($"/api/dogadjaji?sort={Uri.EscapeDataString(sort)}&smjer={Uri.EscapeDataString(smjer)}");

        Assert.Equal(HttpStatusCode.BadRequest, odgovor.StatusCode);
    }
}
