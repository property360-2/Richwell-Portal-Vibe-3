"""Test suite for the core application."""
from django.test import TestCase
from django.urls import reverse


class CoreViewsTests(TestCase):
    def test_healthcheck_returns_ok(self) -> None:
        response = self.client.get(reverse("healthcheck"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_home_page_renders(self) -> None:
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("Richwell College Portal", response.content.decode())
