#!/usr/bin/env bash
# Pokreće automatsku provjeru zadataka (provjera.sql) za domenu iz .env.
set -uo pipefail
# shellcheck source=zajednicko.sh
source /skripte/zajednicko.sh

cekaj_server

echo "Provjera zadataka – domena: $DOMENA, baza: $BAZA, prijava: $ADMIN_LOGIN"
echo
sqlcmd_admin -d master -i /skripte/provjera.sql \
  -v BAZA="$BAZA" GLAVNA="$GLAVNA" VLASNIK="$VLASNIK" APP="$APP" DOMENA="$DOMENA"
