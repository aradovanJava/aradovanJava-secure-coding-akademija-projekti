// @@VULN S07
using System.Security.Cryptography;
using System.Text;
// @@SECURE S07
using Microsoft.AspNetCore.Identity;
// @@END S07

namespace MedTermin.Api.Autentikacija;

/// <summary>Izračun i provjera sažetka lozinke (stupac <c>korisnici.password_hash</c>).</summary>
public sealed class LozinkeServis
{
// @@VULN S07
    public string Hashiraj(string lozinka) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(lozinka))).ToLowerInvariant();

    public bool Provjeri(string spremljeniHash, string lozinka) =>
        string.Equals(spremljeniHash, Hashiraj(lozinka), StringComparison.Ordinal);
// @@SECURE S07
    private readonly PasswordHasher<PrijavljeniKorisnik> _hasher = new();

    public string Hashiraj(string lozinka) => _hasher.HashPassword(null!, lozinka);

    public bool Provjeri(string spremljeniHash, string lozinka)
    {
        try
        {
            return _hasher.VerifyHashedPassword(null!, spremljeniHash, lozinka) != PasswordVerificationResult.Failed;
        }
        catch (FormatException)
        {
            return false;
        }
    }
// @@END S07
}
