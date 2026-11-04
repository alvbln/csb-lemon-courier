# Lemon Courier — CSB MOOC 2026 project (deliberately insecure)

Coursework for the University of Helsinki course "Introduction to Cyber Security: MOOC 2026" (TKT200094).

A small parcel-courier web application (Python 3 + Django 5.2) that **intentionally contains
security flaws** from the OWASP Top 10 (2021 list). Every flaw is marked with `FLAW <n>` comments
and its fix is provided as **commented-out code right next to it** (the official course rule:
one version, fixes commented out, no git branches for fixes).

The subdirectory `fix/` contains the SAME application with all fixes applied; use it to walk
through the fix screenshots (`flaw-N-after.png`).

## Install & run (Windows / Linux / macOS)

Requirements: Python 3.10+ and internet access for pip.

```
python3 -m venv venv                 # Windows: python -m venv venv
source venv/bin/activate             # Windows: venv\Scripts\activate
pip install Django==5.2.19
python manage.py migrate
python seed.py                       # creates users bob/alice + demo shipment
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and log in as `bob` / `secret123` (or `alice` / `pw2`).
For the fixed version: `cd fix && python manage.py runserver`.

## The five flaws (OWASP Top 10: 2021 list, no mix)

| # | OWASP 2021 | Where | Effect |
|---|-----------|-------|--------|
| 1 | A01:2021 Broken Access Control | `flawapp/views.py` indexView / listallView / addView / deleteView | every user sees all shipments incl. release PINs, can create records for others and delete others' records |
| 2 | A02:2021 Cryptographic Failures | `flawapp/views.py` registerView / loginView / releaseView; `flawapp/models.py` | passwords and the release PIN are stored and compared as cleartext |
| 3 | A03:2021 Injection | `flawapp/views.py` releaseView | raw SQL built by string concatenation → UNION-based SQL injection; DB errors are returned to the client |
| 4 | A07:2021 Identification and Authentication Failures | `flawapp/views.py` loginView | unlimited brute-force/dictionary guessing: no throttling, lockout or logging |
| 5 | A05:2021 Security Misconfiguration | `csbproj/settings.py`, `flawapp/views.py` releaseView | hard-coded SECRET_KEY, DEBUG=True, ALLOWED_HOSTS=*, stack traces/exception details to users, no security logging |

## Demo cheat-sheet (flawed server on :8000)

```
# A01: other users' data + their PINs
curl -s -b "$COOKIES" http://127.0.0.1:8000/listall/
# A02: the value stored in the password column IS the working password
curl -d "username=clearbob&password=<value-from-db>" http://127.0.0.1:8000/login/
# A03: open the locker without knowing the PIN (auth=not needed)
curl -d "tracking_code=x' UNION SELECT 1,'0000' -- &release_pin=0000" http://127.0.0.1:8000/release/
# A03b/A05: error-based leak
curl -d "tracking_code=x' NOSQL&release_pin=1" http://127.0.0.1:8000/release/
# A01: cross-user delete
curl -b "$COOKIES" -d "id=1" http://127.0.0.1:8000/delete/
```

`probe2.py` reproduces all of the above against a running dev server (Django test client).

## Screenshots

`screenshots/flaw-N-before-1.png` (effect of the flaw) and `screenshots/flaw-N-after-1.png`
(effect after the fix) for N=1..5, as required by the course.
