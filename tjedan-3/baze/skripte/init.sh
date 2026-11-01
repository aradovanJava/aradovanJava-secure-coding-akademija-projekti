#!/usr/bin/env bash
# Stvara bazu odabrane domene i zatečene postavke – samo ako baza još ne postoji.
set -euo pipefail
# shellcheck source=zajednicko.sh
source /skripte/zajednicko.sh

cekaj_server

postoji=$(sqlcmd_admin -h -1 -W -Q "SET NOCOUNT ON; SELECT CASE WHEN DB_ID(N'$BAZA') IS NULL THEN 0 ELSE 1 END;" | tr -d '[:space:]')
if [ "$postoji" = "1" ]; then
  echo "Baza $BAZA već postoji – inicijalizacija se preskače (reset: docker compose down -v)."
  exit 0
fi

echo "== Stvaram bazu $BAZA (domena $DOMENA) =="
sqlcmd_admin -i "/skripte/postavljanje/$DOMENA.sql"
echo "== Primjenjujem zatečene postavke tima =="
sqlcmd_admin -i /skripte/postavljanje/zatecene-postavke.sql \
  -v BAZA="$BAZA" DOMENA="$DOMENA" APP="$APP"
echo "Gotovo: baza $BAZA je spremna. Spojite se na localhost,${SQL_PORT:-1433} i krenite od ZADACI.md."
