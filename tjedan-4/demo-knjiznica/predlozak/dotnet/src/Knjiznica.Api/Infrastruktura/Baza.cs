using Microsoft.Data.Sqlite;

namespace Knjiznica.Api.Infrastruktura;

/// <summary>
/// Baza u memoriji (SQLite): jedna otvorena veza po instanci aplikacije, pa svaka instanca (i svaki
/// <c>WebApplicationFactory</c> u testovima) dobiva svježu bazu. Pristup je serijaliziran bravom.
/// </summary>
public sealed class Baza : IDisposable
{
    private const string Shema = """
        CREATE TABLE korisnici (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            korisnicko_ime TEXT NOT NULL UNIQUE,
            lozinka_hash   TEXT NOT NULL,
            uloga          TEXT NOT NULL,
            ime            TEXT NOT NULL,
            email          TEXT NOT NULL,
            adresa         TEXT NOT NULL DEFAULT '',
            telefon        TEXT NOT NULL DEFAULT '',
            clanarina      TEXT NOT NULL DEFAULT 'AKTIVNA'
        );
        CREATE TABLE knjige (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            naslov   TEXT NOT NULL,
            autor    TEXT NOT NULL,
            godina   INTEGER NOT NULL,
            skrivena INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE posudbe (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            korisnik_id INTEGER NOT NULL REFERENCES korisnici (id),
            knjiga_id   INTEGER NOT NULL REFERENCES knjige (id),
            rok         TEXT NOT NULL,
            produzenja  INTEGER NOT NULL DEFAULT 0
        );
        """;

    private readonly SqliteConnection _veza = new("Data Source=:memory:");
    private readonly Lock _brava = new();

    public Baza()
    {
        _veza.Open();
        Izvrsi(Shema);
    }

    /// <summary>SELECT – retci kao rječnici (naziv stupca → vrijednost).</summary>
    public List<Dictionary<string, object?>> Upit(string sql, params (string Naziv, object? Vrijednost)[] parametri)
    {
        lock (_brava)
        {
            using var naredba = Naredba(sql, parametri);
            using var citac = naredba.ExecuteReader();
            var redovi = new List<Dictionary<string, object?>>();
            while (citac.Read())
            {
                var red = new Dictionary<string, object?>(StringComparer.OrdinalIgnoreCase);
                for (var i = 0; i < citac.FieldCount; i++)
                {
                    red[citac.GetName(i)] = citac.IsDBNull(i) ? null : citac.GetValue(i);
                }
                redovi.Add(red);
            }
            return redovi;
        }
    }

    public Dictionary<string, object?>? Jedan(string sql, params (string Naziv, object? Vrijednost)[] parametri) =>
        Upit(sql, parametri).FirstOrDefault();

    /// <summary>INSERT/UPDATE/DELETE – vraća broj promijenjenih redaka.</summary>
    public int Izvrsi(string sql, params (string Naziv, object? Vrijednost)[] parametri)
    {
        lock (_brava)
        {
            using var naredba = Naredba(sql, parametri);
            return naredba.ExecuteNonQuery();
        }
    }

    /// <summary>INSERT – vraća ID novog retka.</summary>
    public long Umetni(string sql, params (string Naziv, object? Vrijednost)[] parametri)
    {
        lock (_brava)
        {
            using (var naredba = Naredba(sql, parametri))
            {
                naredba.ExecuteNonQuery();
            }
            using var id = Naredba("SELECT last_insert_rowid()", []);
            return (long)id.ExecuteScalar()!;
        }
    }

    private SqliteCommand Naredba(string sql, (string Naziv, object? Vrijednost)[] parametri)
    {
        var naredba = _veza.CreateCommand();
        naredba.CommandText = sql;
        foreach (var (naziv, vrijednost) in parametri)
        {
            naredba.Parameters.AddWithValue(naziv, vrijednost ?? DBNull.Value);
        }
        return naredba;
    }

    public void Dispose() => _veza.Dispose();
}
