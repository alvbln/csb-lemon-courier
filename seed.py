#!/usr/bin/env python3
"""Create the demo database: users bob/alice and one shipment LEMON001 (PIN 1234)."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csbproj.settings")
django.setup()
from django.contrib.auth.models import User
from flawapp.models import Shipment, TrackingEvent

User.objects.all().delete()
Shipment.objects.all().delete()
b = User(username="bob"); b.set_password("secret123"); b.save()
a = User(username="alice"); a.set_password("pw2"); a.save()
s = Shipment.objects.create(owner=b, tracking_code="LEMON001", destination="Teststr 1", release_pin="1234")
TrackingEvent.objects.create(shipment=s, note="Picked up at depot")
print("seeded bob+alice+LEMON001")
