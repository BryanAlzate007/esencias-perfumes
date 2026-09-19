import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.perfumes.models import Perfume
from apps.reviews.models import Sentiment

User = get_user_model()


class AllauthAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_login_logout_and_me(self):
        signup = self.client.post(
            "/_allauth/browser/v1/auth/signup",
            data=json.dumps(
                {
                    "username": "bryan",
                    "email": "bryan@example.com",
                    "password": "StrongPass123!",
                    "first_name": "Bryan",
                    "country": "Colombia",
                }
            ),
            content_type="application/json",
        )
        self.assertIn(signup.status_code, (200, 401), signup.content)
        payload = signup.json()
        self.assertTrue(payload.get("meta", {}).get("is_authenticated") or payload.get("status") in (200, 401))

        user = User.objects.get(username="bryan")
        self.assertEqual(user.profile.country, "Colombia")
        self.assertEqual(user.profile.role, Profile.Role.CUSTOMER)

        self.client.logout()
        login = self.client.post(
            "/_allauth/browser/v1/auth/login",
            data=json.dumps({"username": "bryan", "password": "StrongPass123!"}),
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200, login.content)
        self.assertTrue(login.json()["meta"]["is_authenticated"])

        me = self.client.get("/api/v1/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["username"], "bryan")
        self.assertEqual(me.json()["role"], "customer")

        logout = self.client.delete("/_allauth/browser/v1/auth/session")
        self.assertIn(logout.status_code, (200, 401), logout.content)
        me_after = self.client.get("/api/v1/me/")
        self.assertEqual(me_after.status_code, 403)


class CatalogAndReviewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="Admin1234!",
            is_staff=True,
        )
        self.admin.profile.role = Profile.Role.ADMIN
        self.admin.profile.save()
        self.user = User.objects.create_user(
            username="sofia",
            email="sofia@example.com",
            password="User1234!",
        )
        self.perfume = Perfume.objects.create(
            name="Noche",
            brand="Esencias",
            description="Amaderada",
            image_url="https://example.com/n.jpg",
            price="80.00",
        )

    def test_catalog_is_public(self):
        response = self.client.get("/api/v1/perfumes/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json()["count"], 1)

    def test_customer_cannot_create_perfume(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/api/v1/perfumes/",
            data={"name": "X", "brand": "Y", "description": "Z", "image_url": "https://example.com/x.jpg", "price": "10"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_perfume(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/v1/perfumes/",
            data={
                "name": "Aurora",
                "brand": "Esencias",
                "description": "Cítrica",
                "image_url": "https://example.com/a.jpg",
                "price": "70.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)

    def test_rating_and_review_require_auth(self):
        denied = self.client.post(
            f"/api/v1/perfumes/{self.perfume.id}/rating/",
            data={"sentiment": Sentiment.LOVE},
            format="json",
        )
        self.assertEqual(denied.status_code, 403)
        self.client.force_login(self.user)
        rating = self.client.post(
            f"/api/v1/perfumes/{self.perfume.id}/rating/",
            data={"sentiment": Sentiment.LOVE},
            format="json",
        )
        self.assertEqual(rating.status_code, 200)
        self.assertEqual(rating.json()["rating_counts"]["love"], 1)
        review = self.client.post(
            f"/api/v1/perfumes/{self.perfume.id}/reviews/",
            data={"body": "Excelente para la noche."},
            format="json",
        )
        self.assertEqual(review.status_code, 201)
