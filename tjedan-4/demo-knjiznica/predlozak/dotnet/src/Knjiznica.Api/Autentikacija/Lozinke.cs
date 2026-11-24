using System.Globalization;
using System.Security.Cryptography;
using System.Text;

namespace Knjiznica.Api.Autentikacija;

/// <summary>Pohrana i provjera lozinki korisnika.</summary>
public sealed class Lozinke
{
    // @@VULN K04
    public string Hashiraj(string lozinka) =>
        Convert.ToHexString(MD5.HashData(Encoding.UTF8.GetBytes(lozinka))).ToLowerInvariant();

    public bool Provjeri(string lozinka, string pohranjeno) => Hashiraj(lozinka) == pohranjeno;
    // @@SECURE K04
    private const string Algoritam = "pbkdf2_sha256";
    private const int Iteracije = 600_000;

    /// <summary>PBKDF2-HMAC-SHA256 s nasumičnom solju od 16 bajtova (OWASP: najmanje 600 000 iteracija).</summary>
    public string Hashiraj(string lozinka)
    {
        var sol = RandomNumberGenerator.GetBytes(16);
        var izvedeno = Rfc2898DeriveBytes.Pbkdf2(Encoding.UTF8.GetBytes(lozinka), sol, Iteracije, HashAlgorithmName.SHA256, 32);
        return string.Join('$', Algoritam, Iteracije.ToString(CultureInfo.InvariantCulture),
            Convert.ToBase64String(sol), Convert.ToBase64String(izvedeno));
    }

    public bool Provjeri(string lozinka, string pohranjeno)
    {
        var dijelovi = pohranjeno.Split('$');
        if (dijelovi.Length != 4 || dijelovi[0] != Algoritam)
        {
            return false;
        }
        var sol = Convert.FromBase64String(dijelovi[2]);
        var ocekivano = Convert.FromBase64String(dijelovi[3]);
        var izvedeno = Rfc2898DeriveBytes.Pbkdf2(Encoding.UTF8.GetBytes(lozinka), sol,
            int.Parse(dijelovi[1], CultureInfo.InvariantCulture), HashAlgorithmName.SHA256, ocekivano.Length);
        // usporedba u konstantnom vremenu
        return CryptographicOperations.FixedTimeEquals(izvedeno, ocekivano);
    }
    // @@END K04
}
