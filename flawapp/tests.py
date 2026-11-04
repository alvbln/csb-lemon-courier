from django.test import Client, TestCase
from django.contrib.auth.models import User
from flawapp.models import Shipment


class FlawDemoTests(TestCase):
    def setUp(self):
        self.bob = User(username="bob")
        self.bob.set_password("rightpw")
        self.bob.save()
        Shipment.objects.create(owner=self.bob, tracking_code="LEMON001", destination="Teststr 1", release_pin="1234")

    def test_clear_text_login_flaw(self):
        """FLAW 2: password stored as cleartext, so the raw string equals the DB column."""
        self.bob.password = "rightpw"  # simulate cleartext storage (registerView stores it that way)
        self.bob.save()
        c = Client()
        r = c.post("/login/", {"username": "bob", "password": "rightpw"})
        self.assertEqual(r.status_code, 302)  # flaw: works through cleartext compare

    def test_listall_is_open_to_every_user(self):
        """FLAW 1c: /listall/ dumps all shipments of all users to any logged-in user."""
        User(username="mallory", password="pw").save()
        c = Client()
        c.post("/login/", {"username": "mallory", "password": "pw"})
        r = c.get("/listall/")
        self.assertContains(r, "LEMON001")
        self.assertContains(r, "1234")  # PIN leak

    def test_unreachable_code_in_views(self):
        """Sanity: the file has the deliberate unreachable-fix pattern."""
        import flawapp.views as v
        src = open(v.__file__).read()
        self.assertIn("Database error", src)
