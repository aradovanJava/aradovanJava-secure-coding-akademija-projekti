# Demo „Aplikacija i baza” (Python) – slika za: docker compose --profile aplikacija run --rm aplikacija-python
FROM python:3.13-slim
# mssql-python nosi vlastiti ODBC upravljački program; na Debianu treba još libltdl i Kerberos biblioteke.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libltdl7 libkrb5-3 libgssapi-krb5-2 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY demo.py .
# Ne pokrećemo kao root.
USER nobody
ENTRYPOINT ["python", "demo.py"]
