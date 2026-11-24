"""Oznake sigurnosnih testova: pytest -m sigurnosni, pytest -m k01 …"""


def pytest_configure(config):
    config.addinivalue_line("markers", "sigurnosni: sigurnosni testovi (crveno → zeleno)")
    for i in range(1, 9):
        config.addinivalue_line("markers", f"k0{i}: sigurnosni testovi za ranjivost K0{i}")
