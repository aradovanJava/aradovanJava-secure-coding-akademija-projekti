"""Postavke i tajne: bez API ključa aplikacija se ne pokreće; CORS bez *; https izvan razvoja."""

import pytest
from pydantic import ValidationError

from okviri.aplikacija import napravi_aplikaciju
from okviri.postavke import Postavke
from tests.conftest import TESTNI_API_KLJUC, postavke


def test_bez_api_kljuca_aplikacija_se_ne_pokrece(monkeypatch):
    monkeypatch.delenv("OKVIRI_OBAVIJESTI_API_KLJUC", raising=False)
    with pytest.raises(ValidationError) as greska:
        napravi_aplikaciju(Postavke(_env_file=None, zahtijevaj_https=False))
    assert "obavijesti_api_kljuc" in str(greska.value)


def test_prekratak_api_kljuc_nije_dopusten():
    with pytest.raises(ValidationError):
        postavke(obavijesti_api_kljuc="kratko")


def test_tajna_se_ne_ispisuje():
    p = postavke()
    assert TESTNI_API_KLJUC not in repr(p) and TESTNI_API_KLJUC not in str(p.model_dump())
    assert p.obavijesti_api_kljuc.get_secret_value() == TESTNI_API_KLJUC


def test_cors_ne_smije_biti_zvjezdica():
    with pytest.raises(ValidationError):
        postavke(cors_dopusteni_origini=["*"])


def test_izvan_razvoja_issuer_mora_biti_https():
    with pytest.raises(ValidationError):
        postavke(zahtijevaj_https=True)
    p = postavke(zahtijevaj_https=True, keycloak_issuer="https://sso.primjer.hr/realms/akademija")
    assert p.jwks_url == "https://sso.primjer.hr/realms/akademija/protocol/openid-connect/certs"


def test_postavke_iz_varijabli_okruzenja(monkeypatch):
    monkeypatch.setenv("OKVIRI_OBAVIJESTI_API_KLJUC", "kljuc-iz-okruzenja-0123")
    monkeypatch.setenv("OKVIRI_ZAHTIJEVAJ_HTTPS", "false")
    monkeypatch.setenv("OKVIRI_CORS_DOPUSTENI_ORIGINI", "http://localhost:5173, https://app.primjer.hr")
    p = Postavke(_env_file=None)
    assert p.cors_dopusteni_origini == ["http://localhost:5173", "https://app.primjer.hr"]
    assert p.obavijesti_api_kljuc.get_secret_value() == "kljuc-iz-okruzenja-0123"
