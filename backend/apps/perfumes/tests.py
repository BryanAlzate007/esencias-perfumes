from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.accounts.models import Profile_person
from apps.perfumes.models import Container, Main_chords, Perfume

User = get_user_model()


class PerfumeCatalogTests(TestCase):
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
        self.chord = Main_chords.objects.create(name="Amaderado", description="Notas de madera")

    def test_admin_can_create_perfume_with_relations(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/v1/perfumes/",
            data={
                "name": "Aurora",
                "brand": "Esencias",
                "description": "Cítrica",
                "notes": "Bergamota",
                "image_url": "https://example.com/a.jpg",
                "price": "70.00",
                "price_usd": "18.50",
                "color": "Ámbar",
                "main_chords": [self.chord.id],
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        perfume = Perfume.objects.get(name="Aurora")
        self.assertEqual(perfume.color, "Ámbar")
        self.assertEqual(list(perfume.main_chords.values_list("id", flat=True)), [self.chord.id])
        self.assertEqual(response.json()["main_chords"], [self.chord.id])

    def test_admin_can_list_main_chords(self):
        self.client.force_login(self.admin)
        response = self.client.get("/api/v1/main-chords/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Amaderado")

    def test_admin_can_manage_lookup_catalogs(self):
        self.client.force_login(self.admin)
        chord = self.client.post(
            "/api/v1/main-chords/",
            data={"name": "Cítrico", "description": "Notas frescas"},
            format="json",
        )
        self.assertEqual(chord.status_code, 201, chord.content)

        container = self.client.post(
            "/api/v1/containers/",
            data={
                "name": "Frasco 50 ml",
                "description": "Vidrio ámbar",
                "image_url": "https://example.com/frasco.jpg",
                "type": "Frasco",
                "size": "50 ml",
                "weight": "120 g",
                "volume": "50 ml",
                "material": "Vidrio",
                "color": "Ámbar",
                "main_chords": [self.chord.id],
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(container.status_code, 201, container.content)
        self.assertEqual(Container.objects.get(name="Frasco 50 ml").main_chords.count(), 1)

        person = self.client.post(
            "/api/v1/profile-persons/",
            data={"name": "Nocturna", "description": "Prefiere notas intensas"},
            format="json",
        )
        self.assertEqual(person.status_code, 201, person.content)
        self.assertEqual(Profile_person.objects.filter(name="Nocturna").count(), 1)
