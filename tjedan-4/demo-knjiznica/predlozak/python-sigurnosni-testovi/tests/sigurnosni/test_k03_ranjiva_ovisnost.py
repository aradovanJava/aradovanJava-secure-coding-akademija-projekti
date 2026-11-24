"""K03 – A03 Software Supply Chain Failures: ranjiva verzija PyYAML-a (CVE-2020-14343) i nesigurno učitavanje."""

import re
from pathlib import Path

import pytest
import yaml

import knjiznica

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k03]


def test_k03_pyyaml_je_nadogradjen():
    requirements = (Path(knjiznica.__file__).resolve().parent.parent / "requirements.txt").read_text("utf-8")
    pogodak = re.search(r"(?im)^\s*pyyaml\s*==\s*(\d+)\.(\d+)", requirements)
    assert pogodak is not None, "PyYAML nije zaključan u requirements.txt"
    assert (int(pogodak.group(1)), int(pogodak.group(2))) >= (6, 0)
    instalirana = tuple(int(x) for x in yaml.__version__.split(".")[:2])
    assert instalirana >= (6, 0), f"instaliran je PyYAML {yaml.__version__}"


def test_k03_yaml_s_python_tagom_vraca_400(klijent, prijava):
    # Tag !!python/... traži od parsera da stvori Python objekt; siguran parser takav dokument odbija.
    katalog = '- naslov: !!python/object/new:builtins.str ["Proba"]\n  autor: Netko\n  godina: 2001\n'
    odgovor = klijent.post(
        "/api/katalog/uvoz", content=katalog.encode("utf-8"),
        headers={**prijava("knjiznicar"), "Content-Type": "application/yaml"},
    )
    assert odgovor.status_code == 400
