"""P2 – Sigurnost baza podataka: novi raspored, Python slajd s demom, bilješke govornika."""
import sys

from pptx import Presentation

from deckkit import biljeske, oblik, postavi_kod, postavi_oznaku, zamijeni_tekst

ULAZ, IZLAZ = sys.argv[1], sys.argv[2]
prs = Presentation(ULAZ)
S = {i + 1: s for i, s in enumerate(prs.slides)}
assert len(S) == 27, len(S)

# ------------------------------------------------------------------ 24: NOVI – Python i demo
zamijeni_tekst(S[24], "Aplikacija i baza", "Aplikacija i baza – Python i demo")
postavi_oznaku(oblik(S[24], 5), "Python", "mssql-python")
postavi_kod(oblik(S[24], 6), [
    "import os",
    "import mssql_python as sql",
    "",
    ('lozinka = os.environ["APP_LOZINKA"]    # nikad u kodu', "h"),
    "veza = sql.connect(",
    '    "Server=localhost,1433;Database=MedTermin;"',
    ('    "UID=medtermin_app;Encrypt=yes;"', "h"),
    '    f"PWD={{{lozinka}}};")   # {…}: smije imati ; i =',
    "kursor = veza.cursor()",
    ("# na početku zahtjeva, nakon prijave korisnika (RLS)", "c"),
    "kursor.execute(",
    ("    \"EXEC sp_set_session_context @key = N'korisnik',\"", "h"),
    ('    " @value = ?, @read_only = 1", korisnik)', "h"),
    ("# vrijednosti uvijek kao parametri", "c"),
    'kursor.execute("SELECT id, termin_id FROM dbo.rezervacije"',
    '               " WHERE pacijent = ?", korisnik)',
])
postavi_oznaku(oblik(S[24], 8), "Demo", "što smije aplikacijski račun (početno stanje)")
postavi_kod(oblik(S[24], 9), [
    ("$ docker compose --profile aplikacija \\", "c"),
    ("      run --rm aplikacija-python", "c"),
    "1. Tko sam u bazi",
    "   član sysadmin ........ DA         [!] Z2.2",
    "   član db_owner ........ DA         [!] Z2.3",
    "2. Što račun stvarno može",
    "   CREATE TABLE ......... DOPUŠTENO  [!] Z3.2",
    "3. Isti unos: x' OR 1=1 --",
    "   parametar (?) ........ 0 redaka",
    "   lijepljenje u upit ... 2 retka    [!] tuđi zapis",
    "4. Row-Level Security",
    "   korisnik ana ......... 2 retka, tuđih: 1  [!]",
    "5. Podrška: OIB 48291736504          [!] Z4.3",
    ("Upozorenja: 12", "h"),
    ("# nakon zadataka Z2–Z4: Upozorenja: 0", "c"),
    ("# isto: aplikacija-java, aplikacija-dotnet", "c"),
])

# ------------------------------------------------------------------ 26: lab – naredba za demo
postavi_kod(oblik(S[26], 6), [
    "cp .env.primjer .env      # postavi DOMENA i lozinke",
    "docker compose up -d      # SQL Server 2022 + baza",
    "docker compose --profile provjera run --rm provjera",
    "docker compose --profile aplikacija run --rm \\",
    "    aplikacija-python     # demo; i -java, -dotnet",
    ("# spajanje: SSMS / VS Code (mssql) na localhost,1433", "c"),
    "docker compose down -v    # potpuni reset",
])
zamijeni_tekst(S[26], "ponovno docker compose up -d.", "ponovno docker compose up -d. Nakon Z2.1 nova lozinka aplikacije ide u .env kao APP_LOZINKA (za demo).",
               obavezno=False)

# ------------------------------------------------------------------ 27: završni slajd
zamijeni_tekst(S[27], "Slijede tri dana nadogradnje vlastitog projekta",
               "Sljedeće (Dan 3): ispitivanje, rizik i usklađenost")

# ------------------------------------------------------------------ bilješke
from biljeske_p2 import BILJESKE  # noqa: E402

assert sorted(BILJESKE) == list(range(1, 28)), sorted(BILJESKE)
for i, tekst in BILJESKE.items():
    biljeske(S[i], tekst)

prs.save(IZLAZ)
print("spremljeno", IZLAZ)
