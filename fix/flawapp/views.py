import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Shipment

# FIX (FLAW 5 / A09 Security Logging & Monitoring Failures): the original app did not log
# any security-relevant event (logins, releases, deletes). Uncomment to enable logging:
# logger = logging.getLogger("lemoncourier")
# handler = logging.FileHandler("security.log")
# handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)


def registerView(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        # FIXED (FLAW 2): salted PBKDF2 hash instead of cleartext storage
        user = User(username=username)
        user.set_password(password)
        user.save()
        # FIX (FLAW 2): hash the password with Django's salted PBKDF2 before storing it
        # user = User(username=username)
        # user.set_password(password)
        # user.save()
        return redirect("/login/")
    return render(request, "flawapp/register.html")


def loginView(request):
    # FIXED (FLAW 4): 5 failed attempts per username -> 10 minute lockout
    from django.core.cache import cache
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if cache.get("login_fails_" + username, 0) >= 5:
            return render(request, "flawapp/login.html",
                          {"error": "Account temporarily locked, try again later"})
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "flawapp/login.html", {"error": "Invalid credentials"})
        # FIXED (FLAW 2): verify the salted hash via Django's authentication machinery
        user = authenticate(request, username=username, password=password)
        if user is not None:
            cache.delete("login_fails_" + username)
            login(request, user)
            return redirect("/")
        # FIXED (FLAW 4): count the failure and remember it for 10 minutes
        cache.set("login_fails_" + username, cache.get("login_fails_" + username, 0) + 1, 600)
        return render(request, "flawapp/login.html", {"error": "Invalid credentials"})
    return render(request, "flawapp/login.html")


@login_required
def indexView(request):
    # FIXED (FLAW 1): only the shipments of the logged-in user
    shipments = Shipment.objects.filter(owner=request.user)
    # FIX (FLAW 1): only the shipments of the logged-in user may leak through
    # shipments = Shipment.objects.filter(owner=request.user)
    return render(request, "flawapp/index.html", {"shipments": shipments})


@login_required
def listallView(request):
    # FIXED (FLAW 1c): only the caller's own records are exposed
    shipments = Shipment.objects.filter(owner=request.user)
    # FIX (FLAW 1c): remove the endpoint entirely (or restrict to staff members)
    # shipments = Shipment.objects.filter(owner=request.user)
    return render(request, "flawapp/listall.html", {"shipments": shipments})


@require_POST
@login_required
def addView(request):
    # FLAW 1b (A01 Broken Access Control): the owner of the new record is taken from a
    # request parameter, so a user can create records for ANYONE else.
    # FIXED (FLAW 1b): the record belongs to the logged-in user, always
    owner = request.user
    code = request.POST.get("tracking_code", "").strip()[:12]
    pin = request.POST.get("release_pin", "").strip()
    if code and pin:
        Shipment.objects.create(owner=owner, tracking_code=code, destination=request.POST.get("destination", ""), release_pin=pin)
    return redirect("/")


@require_POST
def releaseView(request):
    # FLAW 3 (A03 Injection): the raw SQL statement is built by string concatenation, so
    # the tracking_code parameter can change the statement (UNION-based SQL injection).
    code = request.POST.get("tracking_code", "")
    pin = request.POST.get("release_pin", "")
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, release_pin FROM flawapp_shipment WHERE tracking_code = %s", [code])
        row = cursor.fetchone()
    except Exception:
        # FIXED (FLAW 3b): no internals to the client; details would go to the logger (A09)
        return render(request, "flawapp/error.html", status=500)
    if row:
        from django.contrib.auth.hashers import check_password
        if check_password(pin, row[1]):
            return render(request, "flawapp/released.html", {"code": row[0]})
    # comment the two lines above out and the ones below back in for PIN-flaw variant
    return render(request, "flawapp/search.html", {"error": "Invalid tracking code or PIN"})


def searchView(request):
    return render(request, "flawapp/search.html")


@require_POST
@login_required
def deleteView(request):
    # FIXED (FLAW 1d): ownership is enforced
    from django.http import HttpResponseForbidden
    shipment = Shipment.objects.filter(id=request.POST.get("id"), owner=request.user).first()
    if shipment is None:
        return HttpResponseForbidden("Not your shipment")
    shipment.delete()
    return redirect("/")
    # FIX (FLAW 1d): filter by owner and reject if not found
    # from django.http import HttpResponseForbidden
    # shipment = Shipment.objects.filter(id=request.POST.get("id"), owner=request.user).first()
    # if shipment is None:
    #     return HttpResponseForbidden("Not your shipment")
    # shipment.delete()
    # return redirect("/")

def logoutView(request):
    logout(request)
    return redirect("/login/")
