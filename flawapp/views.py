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
        # FLAW 2 (A02 Cryptographic Failures): the password is stored as CLEARTEXT
        user = User(username=username, password=password)
        user.save()
        # FIX (FLAW 2): hash the password with Django's salted PBKDF2 before storing it
        # user = User(username=username)
        # user.set_password(password)
        # user.save()
        return redirect("/login/")
    return render(request, "flawapp/register.html")


def loginView(request):
    # FLAW 4 (A07 Identification and Authentication Failures): the login endpoint can be
    # brute-force unlimited: no throttling, no lockout, no captcha, no delay. An attacker
    # can guess passwords as fast as the server answers (also no logging of failures, see
    # FLAW 5).
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "flawapp/login.html", {"error": "Invalid credentials"})
        # FLAW 2 (A02 Cryptographic Failures): the stored password string is compared in
        # cleartext (it was stored in cleartext, see registerView) instead of verifying a
        # salted hash with Django's authentication machinery.
        if user.password == password:
            login(request, user)
            return redirect("/")
        # FIX (FLAW 4): throttle repeated failures, e.g. with the Django cache:
        # from django.core.cache import cache
        # key = f"login_fails_{username}"
        # fails = cache.get(key, 0)
        # if fails >= 5:
        #     return render(request, "flawapp/login.html", {"error": "Account temporarily locked, try again later"})
        # FIX (FLAW 2): verify the hash and create the session with Django's machinery
        # from django.contrib.auth import authenticate
        # user = authenticate(request, username=username, password=password)
        # if user is not None:
        #     cache.delete(key)
        #     login(request, user)
        #     return redirect("/")
        # cache.set(key, fails + 1, 600)
        return render(request, "flawapp/login.html", {"error": "Invalid credentials"})
    return render(request, "flawapp/login.html")


@login_required
def indexView(request):
    # FLAW 1 (A01 Broken Access Control): the shipment list of EVERY user is rendered for
    # any authenticated user (object-level access rule missing).
    shipments = Shipment.objects.all()
    # FIX (FLAW 1): only the shipments of the logged-in user may leak through
    # shipments = Shipment.objects.filter(owner=request.user)
    return render(request, "flawapp/index.html", {"shipments": shipments})


@login_required
def listallView(request):
    # FLAW 1c (A01 Broken Access Control): a hidden "internal" endpoint that dumps ALL
    # shipments of ALL customers (incl. release PINs) to any logged-in user.
    shipments = Shipment.objects.all()
    # FIX (FLAW 1c): remove the endpoint entirely (or restrict to staff members)
    # shipments = Shipment.objects.filter(owner=request.user)
    return render(request, "flawapp/listall.html", {"shipments": shipments})


@require_POST
@login_required
def addView(request):
    # FLAW 1b (A01 Broken Access Control): the owner of the new record is taken from a
    # request parameter, so a user can create records for ANYONE else.
    owner = request.user
    try:
        owner = User.objects.get(username=request.POST.get("onbehalf"))
    except User.DoesNotExist:
        pass
    # FIX (FLAW 1b): records belong to the logged-in user, always
    # owner = request.user
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
        cursor.execute("SELECT id, release_pin FROM flawapp_shipment WHERE tracking_code = '" + code + "'")
        row = cursor.fetchone()
    except Exception as exc:
        # FLAW 3b (A03 Injection, error-based): internal database errors are handed back
        # to the attacker (also an A05:2021 Security Misconfiguration sub-issue, fixed by
        # the same generic handling).
        return HttpResponse("Database error: " + repr(exc), status=500)
        # FIX (FLAW 3): parameterize the statement and never disclose internal errors
        # cursor.execute("SELECT id, release_pin FROM flawapp_shipment WHERE tracking_code = %s", [code])
        # return render(request, "flawapp/error.html", status=500)
    if row and row[1] == pin:
        # FLAW 2 (A02 Cryptographic Failures): the release PIN is stored and compared as
        # cleartext. FIX (FLAW 2): store only a salted hash: make_password(pin) on insert
        # and check_password(pin, row[1]) here.
        return render(request, "flawapp/released.html", {"code": row[0]})
    return render(request, "flawapp/search.html", {"error": "Invalid tracking code or PIN"})


def searchView(request):
    return render(request, "flawapp/search.html")


@require_POST
@login_required
def deleteView(request):
    # FLAW 1d (A01 Broken Access Control): any logged-in user can delete the shipment of
    # any other user because ownership is never checked.
    shipment = Shipment.objects.get(id=request.POST.get("id"))
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
