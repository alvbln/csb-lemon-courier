# Lemon Courier — CSB MOOC 2026 Project (deliberately insecure)

Coursework for the University of Helsinki course "Introduction to Cyber Security: MOOC 2026" (TKT200094).

A small neighborhood parcel-courier web application that **intentionally contains 5 backend
security flaws** from the OWASP Top 10 (2021 list). Each flaw is marked with
`FLAW <n>` comments and its fix is provided as **commented-out code** right next to it.

## Install

```
python3 -m venv venv
source venv/bin/activate
pip install Django==5.2.19
```

## Initialize the database

```
python manage.py migrate
```

## Run

```
python manage.py runserver
```

Then open http://localhost:8000/ , register two users via the web UI and test.

## The five flaws (OWASP Top 10, 2021 list)

1. A01:2021 Broken Access Control — all-user shipment listing, cross-user create + delete
2. A02:2021 Cryptographic Failures — cleartext password storage, cleartext PIN compare
3. A03:2021 Injection — raw SQL built by string concatenation
4. A05:2021 Security Misconfiguration — DEBUG=True, hard-coded SECRET_KEY, exception details to user
5. A09:2021 Security Logging & Monitoring Failures — no logging of security events (fix = logger)

Screenshots are in `screenshots/` (named flaw-N-before-*.png / flaw-N-after-*.png).
