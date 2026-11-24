"""Pokretanje aplikacije iz IDE-a (desni klik → Run) ili naredbom: python run.py"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("knjiznica.main:app", host="127.0.0.1", port=8000, reload=False)
