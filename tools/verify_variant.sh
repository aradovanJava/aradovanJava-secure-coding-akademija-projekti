#!/usr/bin/env bash
# Provjera jedne varijante: ranjivi slotovi padaju, sigurni prolaze, funkcionalni prolaze.
set -uo pipefail
variant=$1; stack=$2
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
dest="$work/$variant-$stack"
python3 "$root/tools/generate.py" --variant "$variant" --stack "$stack" --dest "$dest" --with-hidden || exit 1
"$root/tools/run_tests.sh" "$stack" "$dest" "$work/res" || exit 1
exp=$(python3 "$root/tools/generate.py" --variant "$variant" --print-vulnerable)
python3 "$root/tools/check_results.py" --results "$work/res" --expect-vulnerable "$exp" --gha --label "$variant $stack"
