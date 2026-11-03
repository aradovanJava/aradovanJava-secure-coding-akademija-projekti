"""Postavke aplikacije (pydantic-settings): varijable okruženja s prefiksom OKVIRI_ ili datoteka .env.

Tajna OKVIRI_OBAVIJESTI_API_KLJUC nije u repozitoriju: lokalno je u .env (u .gitignore), na poslužitelju
u varijabli okruženja ili trezoru. Bez nje se aplikacija ne pokreće (provjera pri pokretanju, fail fast).
"""

from typing import Annotated, Any

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Postavke(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OKVIRI_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # JWT od Keycloaka: potpis (JWKS), iss, aud i rok valjanosti provjerava PyJWT.
    keycloak_issuer: str = "http://localhost:8180/realms/akademija"
    keycloak_audience: str = "medtermin-api"
    # Zadano: <issuer>/protocol/openid-connect/certs (Keycloak). Ključevi se dohvaćaju tek kod prvog tokena.
    keycloak_jwks_url: str | None = None
    # Izvan lokalnog razvoja issuer i JWKS moraju biti na https:// (kao RequireHttpsMetadata u .NET-u).
    zahtijevaj_https: bool = True

    # Isto značenje kao app.cors.allowed-origins u T2; u varijabli okruženja origini su odvojeni zarezom.
    cors_dopusteni_origini: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    # Dopuštene vrijednosti zaglavlja Host (kao AllowedHosts u ASP.NET Coreu).
    dopusteni_hostovi: Annotated[list[str], NoDecode] = ["localhost", "127.0.0.1"]
    # Lokalna prijava: najviše N pokušaja u minuti po IP adresi.
    prijava_pokusaja_u_minuti: int = Field(default=5, ge=1)
    # Swagger UI (/docs) i OpenAPI shema – zadano isključeno, uključite samo lokalno.
    api_dokumentacija: bool = False
    # Strict-Transport-Security – uključite tek kad aplikacija radi iza HTTPS-a.
    hsts: bool = False

    # TAJNA (SecretStr se ne ispisuje u repr/logu). Nema zadane vrijednosti: mora doći iz okruženja ili .env.
    obavijesti_api_kljuc: SecretStr = Field(min_length=16)
    obavijesti_adresa: str = "https://obavijesti.example/api/"

    @field_validator("cors_dopusteni_origini", "dopusteni_hostovi", mode="before")
    @classmethod
    def _popis_odvojen_zarezom(cls, vrijednost: Any) -> Any:
        if isinstance(vrijednost, str):
            return [dio.strip() for dio in vrijednost.split(",") if dio.strip()]
        return vrijednost

    @field_validator("cors_dopusteni_origini")
    @classmethod
    def _bez_zvjezdice(cls, origini: list[str]) -> list[str]:
        if "*" in origini:
            raise ValueError("cors_dopusteni_origini ne smije sadržavati *")
        return origini

    @model_validator(mode="after")
    def _https_izvan_razvoja(self) -> "Postavke":
        if self.zahtijevaj_https:
            for adresa in (self.keycloak_issuer, self.jwks_url):
                if not adresa.startswith("https://"):
                    raise ValueError(f"{adresa} mora biti https:// (lokalni razvoj: OKVIRI_ZAHTIJEVAJ_HTTPS=false)")
        return self

    @property
    def jwks_url(self) -> str:
        return self.keycloak_jwks_url or self.keycloak_issuer.rstrip("/") + "/protocol/openid-connect/certs"
