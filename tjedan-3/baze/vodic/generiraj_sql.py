"""SQL datoteke koraka i testova iz vodiča za jednu domenu (za provjeru u CI-ju).

python3 generiraj_sql.py <domena> <izlazna mapa>
  korak-K1.sql … korak-K9.sql, test-K1.sql … test-K9.sql, ocekivano.txt (kumulativno PROŠLO po koraku)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sadrzaj import KORACI, za_domenu  # noqa: E402

domena, izlaz = sys.argv[1], sys.argv[2]
os.makedirs(izlaz, exist_ok=True)
kumulativno = []
with open(os.path.join(izlaz, "ocekivano.txt"), "w", encoding="utf-8") as oc:
    for k in KORACI:
        with open(os.path.join(izlaz, f"korak-{k['id']}.sql"), "w", encoding="utf-8") as f:
            f.write(":on error exit\nSET NOCOUNT ON;\nGO\n" + za_domenu(k["sql"], domena) + "\n")
        test = za_domenu(k["test"], domena)
        if domena == "medtermin" and k.get("test_medtermin"):
            test += "\nGO\n" + k["test_medtermin"]
        with open(os.path.join(izlaz, f"test-{k['id']}.sql"), "w", encoding="utf-8") as f:
            f.write(":on error exit\nSET NOCOUNT ON;\nGO\n" + test + "\nGO\n")
        kumulativno += k["provjere"]
        oc.write(f"{k['id']} {' '.join(kumulativno)}\n")
print("generirano:", sorted(os.listdir(izlaz)))
