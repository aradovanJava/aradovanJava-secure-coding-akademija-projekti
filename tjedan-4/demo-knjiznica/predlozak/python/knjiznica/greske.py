"""Greške koje API vraća kao JSON oblika {"greska": "..."}."""


class ApiGreska(Exception):
    def __init__(self, status: int, poruka: str) -> None:
        super().__init__(poruka)
        self.status = status
        self.poruka = poruka

    @staticmethod
    def neprijavljen() -> "ApiGreska":
        return ApiGreska(401, "Potrebna je prijava.")

    @staticmethod
    def neispravna_prijava() -> "ApiGreska":
        return ApiGreska(401, "Neispravno korisničko ime ili lozinka.")

    @staticmethod
    def neispravno(poruka: str) -> "ApiGreska":
        return ApiGreska(400, poruka)

    @staticmethod
    def zabranjeno(poruka: str) -> "ApiGreska":
        return ApiGreska(403, poruka)

    @staticmethod
    def nije_pronadjeno(poruka: str) -> "ApiGreska":
        return ApiGreska(404, poruka)

    @staticmethod
    def sukob(poruka: str) -> "ApiGreska":
        return ApiGreska(409, poruka)
