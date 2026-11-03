"""Autorizacija API-ja: 401 bez tokena, samo vlastite rezervacije, 404 za tuđu, ADMIN, zaglavlja, CORS."""

from fastapi.testclient import TestClient

from okviri.sigurnost.ovlasti import javno


def test_health_je_javan(klijent):
    odgovor = klijent.get("/api/health")
    assert odgovor.status_code == 200
    assert odgovor.json() == {"status": "UP"}


def test_bez_tokena_je_401_u_json_formatu(klijent):
    odgovor = klijent.get("/api/rezervacije/moje")
    assert odgovor.status_code == 401
    assert odgovor.headers["WWW-Authenticate"].startswith("Bearer")
    assert odgovor.json() == {"greska": "Potrebna je prijava."}


def test_moje_vraca_samo_rezervacije_prijavljenog_korisnika(klijent, kao):
    odgovor = klijent.get("/api/rezervacije/moje", headers=kao("ana", "KORISNIK"))
    assert odgovor.status_code == 200
    assert [r["id"] for r in odgovor.json()] == [1, 3]
    assert {r["pacijent"] for r in odgovor.json()} == {"ana"}
    assert odgovor.json()[0] == {"id": 1, "pacijent": "ana", "terminId": 1, "napomena": "Kontrolni pregled tlaka"}


def test_tuda_rezervacija_se_ne_brise_i_404(klijent, kao, app):
    odgovor = klijent.delete("/api/rezervacije/1", headers=kao("marko", "KORISNIK"))
    assert odgovor.status_code == 404
    assert odgovor.json() == {"greska": "Zapis nije pronađen."}
    assert app.state.rezervacije.pronadi(1) is not None
    assert app.state.obavijesti.poslano == 0


def test_nepostojeca_isto_404_kao_tuda(klijent, kao):
    assert klijent.delete("/api/rezervacije/999", headers=kao("marko", "KORISNIK")).status_code == 404


def test_vlasnik_brise_svoju(klijent, kao, app):
    assert klijent.delete("/api/rezervacije/3", headers=kao("ana", "KORISNIK")).status_code == 204
    assert [r["id"] for r in klijent.get("/api/rezervacije/moje", headers=kao("ana", "KORISNIK")).json()] == [1]
    assert app.state.obavijesti.poslano == 1


def test_admin_brise_bilo_koju(klijent, kao, app):
    assert klijent.delete("/api/rezervacije/2", headers=kao("admin", "ADMIN")).status_code == 204
    assert app.state.rezervacije.pronadi(2) is None


def test_adminski_popis_samo_za_admina(klijent, kao):
    ana = klijent.get("/api/admin/rezervacije", headers=kao("ana", "KORISNIK"))
    assert ana.status_code == 403
    assert ana.json() == {"greska": "Nemate ovlasti za ovu radnju."}
    admin = klijent.get("/api/admin/rezervacije", headers=kao("admin", "ADMIN"))
    assert admin.status_code == 200
    assert len(admin.json()) == 3


def test_uloga_iz_tijela_zahtjeva_ili_parametra_ne_vrijedi(klijent, kao):
    # Uloge dolaze samo iz potpisanog tokena (realm_access.roles).
    odgovor = klijent.get("/api/admin/rezervacije?uloga=ADMIN", headers={**kao("ana", "KORISNIK"), "X-Uloga": "ADMIN"})
    assert odgovor.status_code == 403


JAVNE_RUTE = {("GET", "/api/health"), ("POST", "/api/auth/login")}


def test_zadano_zabranjeno_za_svaku_rutu_osim_izricito_javnih(app, klijent):
    """Svaka ruta iz OpenAPI sheme bez tokena vraća 401 – osim popisa javnih (nova javna ruta = svjesna odluka)."""
    rute = {(m.upper(), p) for p, operacije in app.openapi()["paths"].items() for m in operacije}
    assert JAVNE_RUTE <= rute
    for metoda, putanja in sorted(rute - JAVNE_RUTE):
        odgovor = klijent.request(metoda, putanja.replace("{id}", "1"), json={})
        assert odgovor.status_code == 401, f"{metoda} {putanja}"
    for metoda, putanja in JAVNE_RUTE:
        assert klijent.request(metoda, putanja, json={}).status_code != 401


def test_nova_ruta_bez_ovisnosti_je_svejedno_zasticena(app, kao):
    @app.get("/api/nova")
    def nova() -> dict:
        return {"ok": True}

    with TestClient(app) as k:
        assert k.get("/api/nova").status_code == 401
        assert k.get("/api/nova", headers=kao("ana", "KORISNIK")).status_code == 200


def test_sigurnosna_zaglavlja_na_svakom_odgovoru(klijent):
    for odgovor in (klijent.get("/api/health"), klijent.get("/api/rezervacije/moje"), klijent.get("/nepostoji")):
        assert odgovor.headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"
        assert odgovor.headers["X-Content-Type-Options"] == "nosniff"
        assert odgovor.headers["X-Frame-Options"] == "DENY"
        assert odgovor.headers["Referrer-Policy"] == "no-referrer"
        assert "no-store" in odgovor.headers["Cache-Control"]
        assert "server" not in {k.lower() for k in odgovor.headers}


def test_cors_samo_za_dopusteni_origin(klijent, kao):
    preflight = {"Access-Control-Request-Method": "GET"}
    dopusten = klijent.options("/api/rezervacije/moje", headers={"Origin": "http://localhost:5173", **preflight})
    assert dopusten.status_code == 200
    assert dopusten.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert "Access-Control-Allow-Credentials" not in dopusten.headers

    zli = klijent.options("/api/rezervacije/moje", headers={"Origin": "https://zlo.example", **preflight})
    assert "Access-Control-Allow-Origin" not in zli.headers

    zli_get = klijent.get("/api/rezervacije/moje", headers={"Origin": "https://zlo.example", **kao("ana", "KORISNIK")})
    assert zli_get.status_code == 200
    assert "Access-Control-Allow-Origin" not in zli_get.headers


def test_nepoznat_host_je_odbijen(app):
    with TestClient(app, base_url="http://zlo.example") as k:
        assert k.get("/api/health").status_code == 400


def test_neocekivana_greska_bez_detalja(app):
    @app.get("/api/kvar")
    @javno
    def kvar() -> dict:
        raise RuntimeError("interni detalj /etc/tajna")

    with TestClient(app, raise_server_exceptions=False) as k:
        odgovor = k.get("/api/kvar")
    assert odgovor.status_code == 500
    assert odgovor.json() == {"greska": "Došlo je do pogreške."}
    assert "RuntimeError" not in odgovor.text and "Traceback" not in odgovor.text
    assert odgovor.headers["X-Content-Type-Options"] == "nosniff"


def test_nepoznata_ruta_json_404(klijent):
    odgovor = klijent.get("/nepostoji")
    assert odgovor.status_code == 404
    assert odgovor.json() == {"greska": "Nije pronađeno."}


def test_swagger_je_zadano_iskljucen(klijent):
    assert klijent.get("/docs").status_code == 404
    assert klijent.get("/openapi.json").status_code == 404
