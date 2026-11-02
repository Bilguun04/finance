from decimal import Decimal

from django.urls import reverse

from finance.testing import FinanceTestCase


class CoreViewTests(FinanceTestCase):
    def test_anonymous_sees_landing_page(self):
        '''
        Unauthenticated users should see the landing page when they visit the index view.
        '''
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing.html")

    def test_authenticated_redirects_to_dashboard(self):
        '''
        Authenticated users should be redirected to the dashboard when they visit the index view.
        '''
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:index"))
        self.assertRedirects(response, reverse("portfolio:dashboard"))

    def test_market_snapshot_contains_expected_data(self):
        '''
        The market snapshot view should contain the expected data for indexes and stocks.
        '''
        response = self.client.get(reverse("core:market_snapshot"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/_market_snapshot.html")
        self.assertIn("indexes", response.context)
        self.assertIn("stocks", response.context)

    def test_market_pulse_contains_expected_data(self):
        '''
        The market pulse view should contain the expected data for indexes, gainers, and losers.
        '''
        response = self.client.get(reverse("core:market_pulse"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/_market_pulse.html")
        self.assertIn("headline", response.context)
        self.assertIn("indexes", response.context)
        self.assertIn("gainers", response.context)
        self.assertIn("losers", response.context)

    def test_landing_page_contains_market_status(self):
        '''
        The landing page should contain the market status and change label.
        '''
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing.html")
        self.assertIn("market_status", response.context)
        self.assertIn("change_label", response.context)