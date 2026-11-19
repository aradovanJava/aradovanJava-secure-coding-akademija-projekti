#!/usr/bin/env bash
# Ponovno stvaranje demo repozitorija za Dan 3 (MedTermin, Python) – SAMO ZA PREDAVAČA.
#   tjedan-3/dan3-demo-python/pripremi-dan3.sh <odredište>
# Rezultat: git repozitorij s istom poviješću kao aradovanJava/t3-dan3-medtermin-demo-python (main) i granama
# nalaz/N-01-istek-sesije, dokaz/regresija-s06, dokaz/regresija-s10. Push i PR-ove napravite ručno (README.md).
set -euo pipefail
odr=$1
ovdje=$(cd "$(dirname "$0")" && pwd)
"$ovdje/../devsecops/test/pripremi.sh" python medtermin all-secure "$odr" >/dev/null
cd "$odr"
git config user.name  "${GIT_AUTHOR_NAME:-Predavač}"
git config user.email "${GIT_AUTHOR_EMAIL:-predavac@example.invalid}"
baza=$(git rev-parse HEAD)
git am -q --committer-date-is-author-date "$ovdje"/zakrpe/000[1-2]-*.patch
testovi=$(git rev-parse HEAD)
git switch -q -c nalaz/N-01-istek-sesije
git am -q --committer-date-is-author-date "$ovdje"/zakrpe/000[3-4]-*.patch
git switch -q main
git merge -q --no-ff -m "Spoji N-01: istek i prekid sesije (test crven → zelen)" nalaz/N-01-istek-sesije
git am -q --committer-date-is-author-date "$ovdje"/zakrpe/0005-*.patch
# Grane za dokaz pada odvajaju se od main prije N-01 (kao u izvornom repozitoriju).
for d in s06 s10; do
  git switch -q -c "dokaz/regresija-$d" "$testovi"
  git am -q --committer-date-is-author-date "$ovdje/dokaz/regresija-$d.patch"
done
git switch -q main
echo "Pripremljeno: $odr (main + nalaz/N-01-istek-sesije, dokaz/regresija-s06, dokaz/regresija-s10; baza $baza)"
