from pathlib import Path
import unittest


class OnboardingWithoutSeoTest(unittest.TestCase):
    def test_onboarding_does_not_offer_or_submit_seo_products(self):
        html = (Path(__file__).parents[1] / "onboarding" / "index.html").read_text(encoding="utf-8")

        forbidden = [
            "SEO & Online-Sichtbarkeit",
            "SEO Basic",
            "SEO Pro",
            "seoPackage",
            "seoPrice",
            "function sseo",
            "seo-basic",
            "seo-pro",
        ]
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, html)

        self.assertIn('data-pkg="starter"', html)
        self.assertIn('data-pkg="pro"', html)
        self.assertIn("webhook/stripe-checkout", html)


if __name__ == "__main__":
    unittest.main()
