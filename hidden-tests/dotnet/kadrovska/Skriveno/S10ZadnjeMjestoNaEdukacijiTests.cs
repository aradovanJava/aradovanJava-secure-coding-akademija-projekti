using System.Net;
using Microsoft.Data.Sqlite;
using Xunit;

namespace Kadrovska.Tests.Skriveno;

/// <summary>S10 se izvodi zasebno (bez paralelnih testova koji opterećuju CPU), da utrka bude deterministična.</summary>
[CollectionDefinition(nameof(S10Zasebno), DisableParallelization = true)]
public sealed class S10Zasebno
{
}

/// <summary>S10 – utrka kod prijave na zadnje mjesto edukacije (edukacija 3: kapacitet 20, prijavljeno 19).</summary>
[Collection(nameof(S10Zasebno))]
[Trait("Category", "Skriveno")]
[Trait("Slot", "S10")]
public sealed class S10ZadnjeMjestoNaEdukacijiTests
{
    private const int BrojZaposlenika = 10;
    private const long EdukacijaId = 3;

    [Fact]
    public async Task IstodobnePrijaveNePrelazeKapacitet()
    {
        // dovoljno dretvi da svih 10 zahtjeva krene istodobno i na sporom CI računalu
        ThreadPool.GetMinThreads(out var radne, out var io);
        ThreadPool.SetMinThreads(Math.Max(radne, 32), Math.Max(io, 32));
        await using var app = new SkrivenoApp();
        var klijenti = new List<HttpClient>();
        for (var i = 0; i < BrojZaposlenika; i++)
        {
            var username = $"utrka.zaposlenik{i}";
            await app.RegistrirajAsync(username, "Lozinka12345!");
            klijenti.Add(await app.KlijentZaAsync(username, "Lozinka12345!"));
        }

        var start = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var zahtjevi = klijenti.Select(async klijent =>
        {
            await start.Task;
            return await klijent.PostAsync($"/api/edukacije/{EdukacijaId}/prijava", null);
        }).ToList();
        start.SetResult();
        var odgovori = await Task.WhenAll(zahtjevi);
        var statusi = odgovori.Select(o => o.StatusCode).ToList();

        long kapacitet, prijavljeno;
        using (var veza = new SqliteConnection(app.ConnectionString))
        {
            veza.Open();
            using var naredba = veza.CreateCommand();
            naredba.CommandText = "SELECT kapacitet, prijavljeno FROM edukacije WHERE id = $id";
            naredba.Parameters.AddWithValue("$id", EdukacijaId);
            using var citac = naredba.ExecuteReader();
            Assert.True(citac.Read());
            kapacitet = citac.GetInt64(0);
            prijavljeno = citac.GetInt64(1);
        }

        Assert.Equal(1, statusi.Count(s => s == HttpStatusCode.Created));
        Assert.Equal(BrojZaposlenika - 1, statusi.Count(s => s == HttpStatusCode.Conflict));
        Assert.Equal(kapacitet, prijavljeno);
    }
}
