using Knjiznica.Api.Autentikacija;

namespace Knjiznica.Api.Infrastruktura;

/// <summary>Početni podaci: četiri korisnika, šest knjiga i četiri posudbe.</summary>
public static class PocetniPodaci
{
    public static void Napuni(IServiceProvider servisi)
    {
        var baza = servisi.GetRequiredService<Baza>();
        var lozinke = servisi.GetRequiredService<Lozinke>();

        (string Ime, string Lozinka, string Uloga, string PunoIme, string Email, string Adresa, string Telefon, string Clanarina)[] korisnici =
        [
            ("ana", "Ana123!", "CLAN", "Ana Anić", "ana.anic@primjer.hr", "Ilica 10, Zagreb", "091 111 1111", "AKTIVNA"),
            ("marko", "Marko123!", "CLAN", "Marko Marić", "marko.maric@primjer.hr", "Vukovarska 22, Zagreb", "092 222 2222", "ISTEKLA"),
            ("iva", "Iva123!", "CLAN", "Iva Ivić", "iva.ivic@primjer.hr", "Savska 5, Zagreb", "095 333 3333", "SUSPENDIRANA"),
            ("knjiznicar", "Knjiga123!", "KNJIZNICAR", "Kata Knjižić", "kata.knjizic@knjiznica.hr", "Trg knjiga 1, Zagreb", "01 444 4444", "AKTIVNA"),
        ];
        foreach (var k in korisnici)
        {
            baza.Umetni(
                "INSERT INTO korisnici (korisnicko_ime, lozinka_hash, uloga, ime, email, adresa, telefon, clanarina) " +
                "VALUES ($ime, $hash, $uloga, $puno, $email, $adresa, $telefon, $clanarina)",
                ("$ime", k.Ime), ("$hash", lozinke.Hashiraj(k.Lozinka)), ("$uloga", k.Uloga), ("$puno", k.PunoIme),
                ("$email", k.Email), ("$adresa", k.Adresa), ("$telefon", k.Telefon), ("$clanarina", k.Clanarina));
        }

        (string Naslov, string Autor, int Godina, int Skrivena)[] knjige =
        [
            ("Proces", "Franz Kafka", 1925, 0),
            ("Na Drini ćuprija", "Ivo Andrić", 1945, 0),
            ("Povratak Filipa Latinovicza", "Miroslav Krleža", 1932, 0),
            ("Zlatarovo zlato", "August Šenoa", 1871, 0),
            ("Čudnovate zgode šegrta Hlapića", "Ivana Brlić-Mažuranić", 1913, 0),
            ("Interni popis za otpis", "Knjižnica", 2026, 1),
        ];
        foreach (var k in knjige)
        {
            baza.Umetni("INSERT INTO knjige (naslov, autor, godina, skrivena) VALUES ($n, $a, $g, $s)",
                ("$n", k.Naslov), ("$a", k.Autor), ("$g", k.Godina), ("$s", k.Skrivena));
        }

        (long Korisnik, long Knjiga)[] posudbe = [(1, 1), (1, 2), (1, 3), (2, 4)];
        foreach (var p in posudbe)
        {
            baza.Umetni("INSERT INTO posudbe (korisnik_id, knjiga_id, rok) VALUES ($k, $kn, '2026-12-10')",
                ("$k", p.Korisnik), ("$kn", p.Knjiga));
        }
    }
}
