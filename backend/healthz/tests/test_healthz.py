from django.test import Client, TestCase
from django.urls import reverse


class HealthzViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_healthz_returns_ok_status(self) -> None:
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("timestamp", payload)
