"""P1 – Sigurnost i zaštita programske potpore i DevSecOps: novi raspored, Python (FastAPI) slajdovi, bilješke."""
import copy
import sys

from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches

from deckkit import (biljeske, oblik, postavi_kod, postavi_odlomke, postavi_odlomke_s_oznakom, postavi_oznaku,
                     zamijeni_tekst)

ULAZ, IZLAZ = sys.argv[1], sys.argv[2]
prs = Presentation(ULAZ)
S = {i + 1: s for i, s in enumerate(prs.slides)}
assert len(S) == 30, len(S)

# ------------------------------------------------------------------ 2: raspored tjedna
okvir = oblik(S[2], 20)
tx = okvir.text_frame._txBody
p = tx.findall(qn("a:p"))
assert [r.text for r in okvir.text_frame.paragraphs[2].runs][0].startswith("Dani 3")
dan1, dan2, dani35, tj4 = (copy.deepcopy(x) for x in p)
for x in p:
    tx.remove(x)


def odlomak(predlozak, oznaka, tekst):
    q = copy.deepcopy(predlozak)
    r = q.findall(qn("a:r"))
    r[0].find(qn("a:t")).text = oznaka
    r[1].find(qn("a:t")).text = tekst
    return q


tx.append(odlomak(dan1, "Dan 1  ", "obrana projekata T2 i ovo predavanje"))
tx.append(odlomak(dan1, "Dan 2  ", "sigurnost baza podataka (SQL Server)"))
tx.append(odlomak(dan2, "Dan 3  ", "radionica: ispitivanje sigurnosti, rizik i usklađenost"))
tx.append(odlomak(dani35, "Dani 4–5  ", "samostalna nadogradnja projekta: pipeline, okviri, baza, usklađenost"))
tx.append(odlomak(tj4, "Tjedan 4  ", "rad na projektu i završni rad s prezentacijom"))

# ------------------------------------------------------------------ 3: ishodi
zamijeni_tekst(S[3], "(Spring Security, ASP.NET Core)", "(Spring Security, ASP.NET Core, FastAPI)")

# ------------------------------------------------------------------ 6: treći stupac FastAPI
lijevi, desni = oblik(S[6], 27), oblik(S[6], 28)
w = Inches(2.92)
lijevi.left, lijevi.width = Inches(0.42), w
desni.left, desni.width = Inches(3.54), w
novi = copy.deepcopy(desni._element)
desni._element.addnext(novi)
novi.find(qn("p:nvSpPr")).find(qn("p:cNvPr")).set("id", "290")
novi.find(qn("p:nvSpPr")).find(qn("p:cNvPr")).set("name", "TextBox FastAPI")
treci = oblik(S[6], 290)
treci.left, treci.width = Inches(6.66), w
for sh in (lijevi, desni, treci):
    sh.height = Inches(1.75)
postavi_odlomke(treci, [
    "FastAPI",
    "ovisnosti (Depends / Security) prije rute; globalna ovisnost u FastAPI(dependencies=[…])",
    "zadano: ništa – prijavu, CORS i zaglavlja dodajete sami (ovisnosti i middleware)",
])

# ------------------------------------------------------------------ 9: NOVI – FastAPI konfiguracija
zamijeni_tekst(S[9], "Konfiguracija u okviru", "Konfiguracija u okviru – Python (FastAPI)")
postavi_oznaku(oblik(S[9], 5), "Python", "FastAPI – zadano zabranjeno")
postavi_kod(oblik(S[9], 6), [
    ("# aplikacija.py – pravilo vrijedi za SVAKU rutu", "c"),
    "app = FastAPI(",
    "    debug=False,",
    ("    dependencies=[Depends(zadano_zabranjeno)],", "h"),
    ")",
    "",
    '@router.get("/api/health")',
    ("@javno            # iznimka se navodi izričito", "h"),
    "def health() -> dict:",
    '    return {"status": "UP"}',
    "",
    ("# bez @javno: ruta traži valjan token", "c"),
    '@router.get("/api/rezervacije/moje")',
    "def moje(korisnik: PrijavljeniKorisnik,",
    "         repo: Repozitorij) -> list[Rezervacija]:",
    "    return repo.za_pacijenta(korisnik.username)",
])
postavi_oznaku(oblik(S[9], 8), "Python", "PyJWT + JWKS (Keycloak)")
postavi_kod(oblik(S[9], 9), [
    ('ALGORITMI = ["RS256"]   # nikad iz zaglavlja tokena', "h"),
    "",
    "def provjeri_token(token, izvor, issuer, audience):",
    ("    kljuc = izvor.get_signing_key_from_jwt(token)", "n"),
    "    claims = jwt.decode(",
    "        token, kljuc.key,",
    ("        algorithms=ALGORITMI,", "h"),
    ("        issuer=issuer, audience=audience,", "h"),
    '        options={"require": ["exp", "iat", "iss", "aud"]},',
    "    )",
    "    return korisnik_iz_tokena(claims)",
    ("    # preferred_username → ime, realm_access.roles → uloge", "c"),
    "",
    ("# JWKS s Keycloaka; ključevi se čuvaju 5 min", "c"),
    "izvor = jwt.PyJWKClient(jwks_url, cache_keys=True,",
    "                        lifespan=300)",
])

# ------------------------------------------------------------------ 10: lozinke – Python redak
kod = oblik(S[10], 6)
postavi_kod(kod, [
    ("// Java: migracija starih hasheva pri prijavi", "c"),
    "PasswordEncoder enc =",
    "  PasswordEncoderFactories.createDelegatingPasswordEncoder();",
    ("// {bcrypt}$2a$10$…   {argon2}…   {sha256}… (stari)", "c"),
    ("// C#: new PasswordHasher<Korisnik>()", "c"),
    ("//     .VerifyHashedPassword(...) == SuccessRehashNeeded", "c"),
    ("# Python (pwdlib): PasswordHash((Argon2Hasher(), …))", "c"),
    ("#     .verify_and_update(lozinka, hash) → (ok, novi_hash)", "c"),
])

# ------------------------------------------------------------------ 15: NOVI – FastAPI vlasništvo
zamijeni_tekst(S[15], "Autorizacija nad objektom (resource-based)", "Autorizacija nad objektom – Python (FastAPI)")
postavi_oznaku(oblik(S[15], 5), "Python", "ovisnost Vlasnistvo")
postavi_kod(oblik(S[15], 6), [
    "class Vlasnistvo[T]:",
    "    def __init__(self, pronadi, vlasnik): ...",
    "",
    "    def __call__(self, id: int, request: Request,",
    "                 korisnik: PrijavljeniKorisnik) -> T:",
    "        zapis = self._pronadi(request, id)",
    "        if zapis is None or not (",
    ("                ADMIN in korisnik.uloge", "h"),
    ("                or self._vlasnik(zapis) == korisnik.username):", "h"),
    ("            raise HTTPException(404, NIJE_PRONADENO)", "h"),
    "        return zapis",
    "",
    "VlastitaRezervacija = Annotated[Rezervacija, Depends(",
    "    Vlasnistvo(pronadi=..., vlasnik=lambda r: r.pacijent))]",
], sz=819)
postavi_oznaku(oblik(S[15], 8), "Python", "ruta bez if-a, uloga na routeru")
postavi_kod(oblik(S[15], 9), [
    '@router.delete("/api/rezervacije/{id}", status_code=204)',
    ("def obrisi(rezervacija: VlastitaRezervacija,", "h"),
    "           repo: Repozitorij) -> Response:",
    "    repo.obrisi(rezervacija.id)   # već provjereno",
    "    return Response(status_code=204)",
    "",
    ("# svaka ruta pod /api/admin traži ulogu ADMIN", "c"),
    "admin_router = APIRouter(",
    '    prefix="/api/admin",',
    ("    dependencies=[Security(prijavljeni_korisnik,", "h"),
    ('                           scopes=["ADMIN"])],', "h"),
    ")",
    "",
    '@admin_router.get("/rezervacije")',
    "def sve(repo: Repozitorij) -> list[Rezervacija]:",
    "    return repo.sve()",
], sz=819)

# ------------------------------------------------------------------ 19: tajne – Python redak
postavi_kod(oblik(S[19], 9), [
    'dotnet user-secrets set "Auth:ClientSecret" "…"',
    "export SPRING_DATASOURCE_PASSWORD=…   # nikad u Git",
    ("# Python: OKVIRI_…_API_KLJUC=… u .env (.gitignore)", "c"),
])

# ------------------------------------------------------------------ 20: NOVI – FastAPI rub aplikacije
zamijeni_tekst(S[20], "Ograničavanje zahtjeva i tajne", "Rub aplikacije i tajne – Python (FastAPI)")
postavi_oznaku(oblik(S[20], 5), "Python", "limits kao FastAPI ovisnost")
postavi_kod(oblik(S[20], 6), [
    "limiter = FixedWindowRateLimiter(MemoryStorage())",
    "limit = RateLimitItemPerMinute(5)",
    "",
    "def ogranicenje_prijave(request: Request) -> None:",
    "    ip = request.client.host",
    ('    if not limiter.hit(limit, "prijava", ip):', "h"),
    ("        raise HTTPException(429, PREVISE_POKUSAJA,", "h"),
    '            headers={"Retry-After": str(sekundi)})',
    "",
    '@router.post("/api/auth/login",',
    ("             dependencies=[Depends(ogranicenje_prijave)])", "h"),
])
postavi_oznaku(oblik(S[20], 8), "Python", "pydantic-settings")
postavi_kod(oblik(S[20], 9), [
    "class Postavke(BaseSettings):   # .env ili okruženje",
    ("    obavijesti_api_kljuc: SecretStr = Field(min_length=16)", "h"),
    ("# nema zadane vrijednosti → bez tajne nema pokretanja", "c"),
])
postavi_odlomke(oblik(S[20], 10), [
    "Rub aplikacije u FastAPI-ju",
    "CORSMiddleware s popisom origina iz postavki; „*” odbijen već pri pokretanju",
    "sigurnosna zaglavlja: vlastiti ASGI middleware za svaki odgovor (FastAPI ih ne dodaje sam)",
    "TrustedHostMiddleware: samo očekivani Host",
    "greške: 400 bez unesenih vrijednosti (zadani 422 vraća i lozinku iz tijela), 500 bez tracebacka, debug=False",
    "Swagger UI (/docs) samo lokalno; tajne kao SecretStr – ne ispisuju se u logu",
])

# ------------------------------------------------------------------ 22: pipeline – Python alati
zamijeni_tekst(S[22], "Semgrep, SpotBugs + FindSecBugs / Roslyn", "Semgrep, SpotBugs + FSB / Roslyn / Bandit")
zamijeni_tekst(S[22], "OSV-Scanner, CycloneDX, Dependabot", "OSV-Scanner, pip-audit, CycloneDX, Dependabot")

# ------------------------------------------------------------------ 29: zadaci
zamijeni_tekst(S[29], "Spring Security / ASP.NET Core", "Spring Security / ASP.NET Core / FastAPI")

# ------------------------------------------------------------------ 30: završni slajd
zamijeni_tekst(S[30], "Sljedeće: Sigurnost baza podataka", "Sljedeće (Dan 2): Sigurnost baza podataka")

# ------------------------------------------------------------------ bilješke govornika
from biljeske_p1 import BILJESKE  # noqa: E402

assert sorted(BILJESKE) == list(range(1, 31)), sorted(BILJESKE)
for i, tekst in BILJESKE.items():
    biljeske(S[i], tekst)

prs.save(IZLAZ)
print("spremljeno", IZLAZ)
