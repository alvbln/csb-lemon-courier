from django.db import models
from django.contrib.auth.models import User


# Lemon Courier - a small neighborhood parcel service.
class Shipment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=12, unique=True)
    destination = models.TextField()
    release_pin = models.CharField(max_length=10)


class TrackingEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
