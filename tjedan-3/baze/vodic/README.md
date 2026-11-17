# Vodič za predavača – Sigurnost baza podataka (samo za predavača)

Rješenja zadataka Z1–Z8 iz paketa „Sigurnost baza podataka”: ključ za analizu Z1 i koraci K1–K9
(uzrok, ispravak u T-SQL-u, testni upit, očekivani rezultat).

| Datoteka | Namjena |
|---|---|
| `sadrzaj.py` | jedini izvor sadržaja (Z1, koraci, SQL, testovi, očekivani rezultati) |
| `generiraj_sql.py` | `python3 generiraj_sql.py <medtermin\|ulaznica\|kadrovska> <mapa>` – korak-K*.sql i test-K*.sql za CI |
| `napravi_docx.js` | Word dokument: `python3 sadrzaj.py sadrzaj.json && node napravi_docx.js sadrzaj.json vodic.docx` (npm paket `docx`) |
| `T3-Baze-rjesenja-Z1-Z8-vodic-za-predavaca.docx` | gotov dokument |

Workflow `.github/workflows/t3-baze-vodic.yml` izvodi sve korake i testove na svježem SQL Serveru 2022
za sve tri domene i provjerava da nakon svakog koraka prolaze očekivane automatske provjere.

Mapa `vodic/` ne smije u studentski paket – `napravi-zip.sh` je odbija.
