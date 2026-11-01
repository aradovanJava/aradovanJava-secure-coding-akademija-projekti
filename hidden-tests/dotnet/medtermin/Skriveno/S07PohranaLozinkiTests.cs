using System.Net;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Data.Sqlite;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S07 – lozinke se ne smiju spremati kao nesoljeni brzi sažetak.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S07")]
public sealed class S07PohranaLozinkiTests
{
    [Fact]
    public async Task IsteLozinkeImajuRazliciteSoljeneSazetke()
    {
        await using var app = new SkrivenoApp();
        const string lozinka = "IstaLozinka123!";
        await app.RegistrirajAsync("hash.prvi", lozinka);
        await app.RegistrirajAsync("hash.drugi", lozinka);

        var sazeci = new Dictionary<string, string>();
        using (var veza = new SqliteConnection(app.ConnectionString))
        {
            veza.Open();
            using var naredba = veza.CreateCommand();
            naredba.CommandText = "SELECT username, password_hash FROM korisnici WHERE username IN ('hash.prvi', 'hash.drugi')";
            using var citac = naredba.ExecuteReader();
            while (citac.Read())
            {
                sazeci[citac.GetString(0)] = citac.GetString(1);
            }
        }

        Assert.Equal(2, sazeci.Count);
        Assert.NotEqual(sazeci["hash.prvi"], sazeci["hash.drugi"]);
        var bajtovi = Encoding.UTF8.GetBytes(lozinka);
        var brziSazeci = new[] { SHA256.HashData(bajtovi), SHA1.HashData(bajtovi), MD5.HashData(bajtovi) }
            .Select(b => Convert.ToHexString(b))
            .Append(lozinka)
            .ToList();
        foreach (var sazetak in sazeci.Values)
        {
            Assert.DoesNotContain(brziSazeci, s => string.Equals(s, sazetak, StringComparison.OrdinalIgnoreCase));
        }

        var prijava = await app.Klijent().PostAsJsonAsync("/api/auth/login", new { username = "hash.prvi", password = lozinka });
        Assert.Equal(HttpStatusCode.OK, prijava.StatusCode);
    }
}
