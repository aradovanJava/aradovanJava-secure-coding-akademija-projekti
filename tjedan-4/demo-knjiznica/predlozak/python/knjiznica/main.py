"""Ulazna točka za uvicorn: uvicorn knjiznica.main:app --port 8000"""

from knjiznica.app import create_app

app = create_app()
