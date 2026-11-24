using System.Collections.Concurrent;
using System.Security.Cryptography;

namespace Knjiznica.Api.Autentikacija;

/// <summary>Nasumični tokeni (32 bajta) izdani pri prijavi; čuvaju se samo u memoriji.</summary>
public sealed class Tokeni
{
    private readonly ConcurrentDictionary<string, long> _tokeni = new();

    public string Izdaj(long korisnikId)
    {
        var token = Convert.ToBase64String(RandomNumberGenerator.GetBytes(32))
            .TrimEnd('=').Replace('+', '-').Replace('/', '_');
        _tokeni[token] = korisnikId;
        return token;
    }

    public long? KorisnikId(string token) => _tokeni.TryGetValue(token, out var id) ? id : null;
}
