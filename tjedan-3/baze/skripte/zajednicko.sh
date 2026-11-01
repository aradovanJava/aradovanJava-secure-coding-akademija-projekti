#!/usr/bin/env bash
# Zajedničke postavke za init.sh i provjera.sh (izvršava se u kontejneru sa slikom mssql/server).

SQLCMD=/opt/mssql-tools18/bin/sqlcmd
SQL_HOST="${SQL_HOST:-sql}"

case "${DOMENA:-}" in
  medtermin) BAZA=MedTermin; GLAVNA=rezervacije; VLASNIK=pacijent ;;
  ulaznica)  BAZA=Ulaznica;  GLAVNA=narudzbe;    VLASNIK=kupac ;;
  kadrovska) BAZA=Kadrovska; GLAVNA=zahtjevi;    VLASNIK=zaposlenik ;;
  *)
    echo "GREŠKA: DOMENA u .env mora biti medtermin, ulaznica ili kadrovska (sada: '${DOMENA:-}')." >&2
    exit 2 ;;
esac
APP="${DOMENA}_app"

ADMIN_LOGIN="${ADMIN_LOGIN:-sa}"
export SQLCMDPASSWORD="${ADMIN_PASSWORD:-${MSSQL_SA_PASSWORD:-}}"

# -C: vjeruj samopotpisanom certifikatu poslužitelja, -b: prekini na grešci,
# -I: QUOTED_IDENTIFIER ON, -f 65001: skripte i ispis u UTF-8.
sqlcmd_admin() {
  "$SQLCMD" -C -S "$SQL_HOST" -U "$ADMIN_LOGIN" -b -I -f 65001 "$@"
}

cekaj_server() {
  for _ in $(seq 1 60); do
    if sqlcmd_admin -l 5 -Q "SELECT 1" -o /dev/null 2>/dev/null; then
      return 0
    fi
    sleep 2
  done
  echo "GREŠKA: ne mogu se prijaviti na SQL Server ($SQL_HOST) kao '$ADMIN_LOGIN'." >&2
  echo "Provjerite ADMIN_LOGIN / ADMIN_PASSWORD (ili MSSQL_SA_PASSWORD) u .env i stanje: docker compose ps" >&2
  sqlcmd_admin -l 5 -Q "SELECT 1" || true
  exit 3
}
