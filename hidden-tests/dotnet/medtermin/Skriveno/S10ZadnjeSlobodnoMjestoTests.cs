using System.Net;
using System.Net.Http.Json;
using Microsoft.Data.Sqlite;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S10 se izvodi zasebno (bez paralelnih testova koji opterećuju CPU), da utrka bude deterministična.</summary>
[CollectionDefinition(nameof(S10Zasebno), DisableParallelization = true)]
public sealed class S10Zasebno
{
}

/// <summary>S10 – utrka kod rezervacije zadnjeg slobodnog termina (termin 7, kapacitet 1).</summary>
[Collection(nameof(S10Zasebno))]
[Trait("Category", "Skriveno")]
[Trait("Slot", "S10")]
public sealed class S10ZadnjeSlobodnoMjestoTests
{
    private const int BrojKorisnika = 10;
    private const long TerminId = 7;

    [Fact]
    public async Task IstodobneRezervacijeNePrelazeKapacitet()
    {
        // dovoljno dretvi da svih 10 zahtjeva krene istodobno i na sporom CI računalu
        ThreadPool.GetMinThreads(out var radne, out var io);
        ThreadPool.SetMinThreads(Math.Max(radne, 32), Math.Max(io, 32));
        await using var app = new SkrivenoApp();
        var klijenti = new List<HttpClient>();
        for (var i = 0; i < BrojKorisnika; i++)
        {
            var username = $"utrka.pacijent{i}";
            await app.RegistrirajAsync(username, "Lozinka12345!");
            klijenti.Add(await app.KlijentZaAsync(username, "Lozinka12345!"));
        }

        var start = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var zahtjevi = klijenti.Select(async klijent =>
        {
            await start.Task;
            return await klijent.PostAsJsonAsync("/api/rezervacije", new { terminId = TerminId, napomena = "Kontrolni pregled", oib = "12345678903" });
        }).ToList();
        start.SetResult();
        var odgovori = await Task.WhenAll(zahtjevi);
        var statusi = odgovori.Select(o => o.StatusCode).ToList();

        long kapacitet, zauzeto, rezervacija;
        using (var veza = new SqliteConnection(app.ConnectionString))
        {
            veza.Open();
            using var naredba = veza.CreateCommand();
            naredba.CommandText = "SELECT kapacitet, zauzeto, (SELECT COUNT(*) FROM rezervacije WHERE termin_id = $id) FROM termini WHERE id = $id";
            naredba.Parameters.AddWithValue("$id", TerminId);
            using var citac = naredba.ExecuteReader();
            Assert.True(citac.Read());
            kapacitet = citac.GetInt64(0);
            zauzeto = citac.GetInt64(1);
            rezervacija = citac.GetInt64(2);
        }

        Assert.Equal(1, statusi.Count(s => s == HttpStatusCode.Created));
        Assert.Equal(BrojKorisnika - 1, statusi.Count(s => s == HttpStatusCode.Conflict));
        Assert.Equal(kapacitet, zauzeto);
        Assert.Equal(1, rezervacija);
    }
}
