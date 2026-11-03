"""Aplikacija za uvicorn: ``uvicorn ulaznica.main:app --reload --port 8000``."""

from ulaznica.app import create_app
from ulaznica.logiranje import nastavi_logiranje

nastavi_logiranje()
app = create_app()
