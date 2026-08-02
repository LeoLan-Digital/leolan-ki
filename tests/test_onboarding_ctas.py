from pathlib import Path
import unittest


class PricingOnboardingLinksTest(unittest.TestCase):
    def test_package_buttons_open_branded_onboarding_with_selected_package(self):
        html = (Path(__file__).parents[1] / "index.html").read_text(encoding="utf-8")

        self.assertIn('href="/onboarding/?paket=starter"', html)
        self.assertIn('href="/onboarding/?paket=pro"', html)
        self.assertNotIn("startCheckout('starter','annual')", html)
        self.assertNotIn("startCheckout('pro','annual')", html)


if __name__ == "__main__":
    unittest.main()
