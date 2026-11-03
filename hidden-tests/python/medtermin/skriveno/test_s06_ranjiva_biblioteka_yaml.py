"""S06 – ranjiva verzija biblioteke za YAML (PyYAML < 5.4, CVE-2020-14343) i učitavanje s tagovima."""

import re
from pathlib import Path

import medtermin


def _requirements() -> str:
    korijen = Path(medtermin.__file__).resolve().parent.parent
    return (korijen / "requirements.txt").read_text(encoding="utf-8")


def test_s06_pyyaml_je_nadogradjen(sk_app):
    pogodak = re.search(r"(?im)^\s*pyyaml\s*(==|>=|~=)\s*(\d+)\.(\d+)", _requirements())
    assert pogodak is not None, "PyYAML nije zaključan u requirements.txt"
    verzija = (int(pogodak.group(2)), int(pogodak.group(3)))
    assert verzija >= (5, 4), f"PyYAML {verzija[0]}.{verzija[1]} ima poznate ranjivosti (CVE-2020-14343)"
    import yaml

    glavna = tuple(int(x) for x in yaml.__version__.split(".")[:2])
    assert glavna >= (5, 4), f"instalirani PyYAML je {yaml.__version__}"


def test_s06_yaml_s_python_tagom_vraca_400(sk_client, sk_prijava):
    dokument = 'podsjetnik: true\nsatiPrije: 24\nkanal: !!python/object/new:builtins.str ["email"]\n'
    odgovor = sk_client.post(
        "/api/postavke", content=dokument, headers={**sk_prijava("marko"), "Content-Type": "application/yaml"}
    )
    assert odgovor.status_code == 400, f"YAML s python/* tagom je prihvaćen ({odgovor.status_code} {odgovor.text})"
