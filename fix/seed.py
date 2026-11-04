#!/usr/bin/env python3
"""Seed the FIXED app's database (same demo data, passwords properly hashed)."""
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
print("fix-tree seeded (hashed credentials)")
