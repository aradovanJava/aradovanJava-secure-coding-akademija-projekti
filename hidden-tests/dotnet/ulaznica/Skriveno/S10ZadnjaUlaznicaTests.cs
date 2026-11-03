using System.Net;
using System.Net.Http.Json;
using Microsoft.Data.Sqlite;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

/// <summary>S10 se izvodi zasebno (bez paralelnih testova koji opterećuju CPU), da utrka bude deterministična.</summary>
[CollectionDefinition(nameof(S10Zasebno), DisableParallelization = true)]
public sealed class S10Zasebno
{
}

/// <summary>S10 – utrka kod kupnje zadnje ulaznice (događaj 5: kapacitet 100, prodano 99).</summary>
[Collection(nameof(S10Zasebno))]
[Trait("Category", "Skriveno")]
[Trait("Slot", "S10")]
public sealed class S10ZadnjaUlaznicaTests
{
    private const int BrojKupaca = 10;
    private const long DogadjajId = 5;

    [Fact]
    public async Task IstodobneKupnjeNePrelazeKapacitet()
    {
        // dovoljno dretvi da svih 10 zahtjeva krene istodobno i na sporom CI računalu
        ThreadPool.GetMinThreads(out var radne, out var io);
        ThreadPool.SetMinThreads(Math.Max(radne, 32), Math.Max(io, 32));
        await using var app = new SkrivenoApp();
        var klijenti = new List<HttpClient>();
        for (var i = 0; i < BrojKupaca; i++)
        {
            var username = $"utrka.kupac{i}";
            await app.RegistrirajAsync(username, "Lozinka12345!");
            klijenti.Add(await app.KlijentZaAsync(username, "Lozinka12345!"));
        }

        var start = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var zahtjevi = klijenti.Select(async klijent =>
        {
            await start.Task;
            return await klijent.PostAsJsonAsync("/api/narudzbe", new { dogadjajId = DogadjajId, kolicina = 1, imeNaUlaznici = "Kupac Test", oib = "12345678903" });
        }).ToList();
        start.SetResult();
        var odgovori = await Task.WhenAll(zahtjevi);
        var statusi = odgovori.Select(o => o.StatusCode).ToList();

        long kapacitet, prodano;
        using (var veza = new SqliteConnection(app.ConnectionString))
        {
            veza.Open();
            using var naredba = veza.CreateCommand();
            naredba.CommandText = "SELECT kapacitet, prodano FROM dogadjaji WHERE id = $id";
            naredba.Parameters.AddWithValue("$id", DogadjajId);
            using var citac = naredba.ExecuteReader();
            Assert.True(citac.Read());
            kapacitet = citac.GetInt64(0);
            prodano = citac.GetInt64(1);
        }

        Assert.Equal(1, statusi.Count(s => s == HttpStatusCode.Created));
        Assert.Equal(BrojKupaca - 1, statusi.Count(s => s == HttpStatusCode.Conflict));
        Assert.Equal(kapacitet, prodano);
    }
}
