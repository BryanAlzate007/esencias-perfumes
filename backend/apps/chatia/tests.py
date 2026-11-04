import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.data_deletion import erase_linked_user
from apps.chatia.models import ChatIA, OlfactoryTest, PerfumeOlfactoryProfile
from apps.chatia.services.olfactory import (
    clean_bridge,
    question_by_number,
    rank,
    tally,
    welcome_text,
)
from apps.perfumes.models import Perfume

User = get_user_model()

MAIL_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_HOST_PASSWORD": "app-password",
    "DEFAULT_FROM_EMAIL": "esencias@localhost",
    "FRONTEND_URL": "http://localhost:5173",
}

CLASSIFY = "apps.chatia.services.advisor.GeminiService.classify"
ADVISE = "apps.chatia.services.advisor.GeminiService.advise"
HIDDEN_OPTION = "Elegante, sofisticada y segura."


def classified(choice="A", bridge="Una loción con presencia te queda bien.", off_topic=False):
    return {"choice": choice, "off_topic": off_topic, "bridge": bridge}


@override_settings(**MAIL_SETTINGS)
class OlfactoryAdvisorTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_welcome_asks_the_first_question_without_options(self):
        sofia = welcome_text("Sofía", "es")
        sebastian = welcome_text("Sebastián", "es")
        self.assertIn("tu asesora comercial", sofia)
        self.assertIn("tu asesor comercial", sebastian)
        self.assertIn("¿Cómo describirías tu personalidad?", sofia)
        self.assertNotIn(HIDDEN_OPTION, sofia)
        self.assertNotIn("Selecciona", sofia)

    def test_bridge_that_copies_an_option_is_discarded(self):
        question = question_by_number(1)
        self.assertEqual(clean_bridge(HIDDEN_OPTION, question), "")
        self.assertEqual(clean_bridge("París es la capital de Francia.", question), "")
        kept = clean_bridge("El resultado es 4. Una loción oriental te queda bien.", question)
        self.assertEqual(kept, "Una loción oriental te queda bien.")

    @patch(CLASSIFY, return_value=classified())
    def test_first_answer_moves_to_the_next_question_without_listing_options(self, _classify):
        response = self.client.post(
            "/api/v1/chat/",
            {"message": "Soy reservada y me gusta pasar desapercibida", "advisor": "Laura", "language": "es"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertIn("¿Qué ambiente disfrutas más?", body["response"])
        self.assertNotIn(HIDDEN_OPTION, body["response"])
        self.assertNotIn("Una playa, el mar", body["response"])
        self.assertNotIn("Selecciona", body["response"])
        self.assertEqual(body["phase"], "question")
        self.assertTrue(body["chat_id"])

    @patch(CLASSIFY)
    def test_off_topic_question_is_not_answered(self, classify):
        response = self.client.post(
            "/api/v1/chat/",
            {"message": "¿Cuál es la capital de Francia?", "advisor": "Sofía", "language": "es"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        text = response.json()["response"]
        self.assertIn("Solo puedo asesorarte sobre lociones y perfumes", text)
        self.assertIn("¿Cómo describirías tu personalidad?", text)
        self.assertNotIn("París", text)
        classify.assert_not_called()

    @patch(CLASSIFY, return_value=classified(choice="A", bridge="El resultado es 4. Una loción oriental te queda bien."))
    def test_model_cannot_smuggle_an_unrelated_answer(self, _classify):
        response = self.client.post(
            "/api/v1/chat/",
            {"message": "Me describo elegante y segura", "advisor": "Sofía", "language": "es"},
            format="json",
        )
        text = response.json()["response"]
        self.assertNotIn("4", text)
        self.assertIn("loción", text)
        self.assertIn("¿Qué ambiente disfrutas más?", text)

    @patch(CLASSIFY, return_value=classified(choice=None, bridge=""))
    def test_keyword_fallback_maps_a_free_answer(self, _classify):
        response = self.client.post(
            "/api/v1/chat/",
            {"message": "Soy elegante, sofisticada y segura", "advisor": "Sofía", "language": "es"},
            format="json",
        )
        self.assertIn("¿Qué ambiente disfrutas más?", response.json()["response"])
        test = OlfactoryTest.objects.get()
        self.assertEqual(test.answers["1"]["choice"], "A")
        self.assertEqual(test.current_question, 2)

    @patch(CLASSIFY, return_value=classified(choice=None, off_topic=True, bridge="La capital es París"))
    def test_classifier_flag_refuses_without_using_its_bridge(self, _classify):
        response = self.client.post(
            "/api/v1/chat/",
            {"message": "cuentame algo que no tenga que ver", "advisor": "Sofía", "language": "es"},
            format="json",
        )
        text = response.json()["response"]
        self.assertIn("Solo puedo asesorarte", text)
        self.assertNotIn("París", text)
        self.assertEqual(OlfactoryTest.objects.get().current_question, 1)

    def test_unknown_chat_is_rejected(self):
        response = self.client.post(
            "/api/v1/chat/",
            {"message": "Hola", "chat_id": str(uuid.uuid4()), "language": "es"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    @patch(ADVISE, return_value="La capital es París")
    @patch(CLASSIFY)
    def test_email_saves_profile_and_sends_result(self, classify, advise):
        classify.return_value = classified()
        Perfume.objects.create(
            name="Aurora",
            brand="Esencias",
            description="Loción oriental",
            notes="Ambar y resinas",
            price="80.00",
            kind=Perfume.Kind.PERFUME,
            is_active=True,
        )
        Perfume.objects.create(
            name="Vela Secreta",
            brand="Esencias",
            description="Vela oriental",
            notes="Ambar y resinas",
            price="40.00",
            kind=Perfume.Kind.CANDLE,
            is_active=True,
        )
        chat_id = None
        for _step in range(10):
            response = self.client.post(
                "/api/v1/chat/",
                {
                    "message": "Elegante, sofisticada y segura",
                    "advisor": "Valentina",
                    "language": "es",
                    **({"chat_id": chat_id} if chat_id else {}),
                },
                format="json",
            )
            self.assertEqual(response.status_code, 200, response.content)
            self.assertNotIn(HIDDEN_OPTION, response.json()["response"])
            chat_id = response.json()["chat_id"]
        self.assertEqual(response.json()["phase"], "email")
        self.assertIn("¿a qué correo te lo mando?", response.json()["response"])
        self.assertIn("Esencias Aurora", response.json()["response"])
        self.assertNotIn("Vela Secreta", response.json()["response"])

        saved = self.client.post(
            "/api/v1/chat/",
            {"message": "Mi correo es Ana@Example.com", "chat_id": chat_id, "language": "es"},
            format="json",
        )
        self.assertEqual(saved.status_code, 200, saved.content)
        self.assertEqual(saved.json()["phase"], "done")
        self.assertIn("ana@example.com", saved.json()["response"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ana@example.com"])
        self.assertIn("Esencias Aurora", mail.outbox[0].body)
        self.assertNotIn("Vela Secreta", mail.outbox[0].body)
        self.assertIn("/perfumes/", mail.outbox[0].body)

        profile = PerfumeOlfactoryProfile.objects.get(email="ana@example.com")
        answers = {str(number): {"choice": "A"} for number in range(1, 11)}
        totals = tally(answers)
        primary, secondary = rank(totals)
        self.assertEqual(profile.primary_family, primary)
        self.assertEqual(profile.secondary_families, secondary)
        self.assertEqual(profile.oriental_score, totals["oriental"])
        self.assertEqual(profile.gourmand_score, totals["gourmand"])
        self.assertEqual(OlfactoryTest.objects.get().status, OlfactoryTest.Status.COMPLETED)
        advise.assert_not_called()

    @patch(CLASSIFY, return_value=classified())
    def test_invalid_email_keeps_asking(self, _classify):
        chat_id = None
        for _step in range(10):
            response = self.client.post(
                "/api/v1/chat/",
                {"message": "A", "language": "es", **({"chat_id": chat_id} if chat_id else {})},
                format="json",
            )
            chat_id = response.json()["chat_id"]
        response = self.client.post(
            "/api/v1/chat/",
            {"message": "luego te lo doy", "chat_id": chat_id, "language": "es"},
            format="json",
        )
        self.assertEqual(response.json()["phase"], "email")
        self.assertIn("correo válido", response.json()["response"])
        self.assertEqual(PerfumeOlfactoryProfile.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    @patch(ADVISE, return_value="La capital es París y nada más.")
    @patch(CLASSIFY, return_value=classified())
    def test_finished_advisor_refuses_topics_outside_lotions(self, _classify, advise):
        chat_id = None
        for _step in range(10):
            response = self.client.post(
                "/api/v1/chat/",
                {"message": "A", "language": "es", **({"chat_id": chat_id} if chat_id else {})},
                format="json",
            )
            chat_id = response.json()["chat_id"]
        self.client.post(
            "/api/v1/chat/",
            {"message": "ana@example.com", "chat_id": chat_id, "language": "es"},
            format="json",
        )
        follow = self.client.post(
            "/api/v1/chat/",
            {"message": "¿Cuál es la capital de Francia?", "chat_id": chat_id, "language": "es"},
            format="json",
        )
        self.assertIn("Solo puedo asesorarte", follow.json()["response"])
        self.assertNotIn("París", follow.json()["response"])
        advise.assert_not_called()

    def test_account_deletion_removes_the_saved_profile(self):
        user = User.objects.create_user("ana", "ana@example.com", "pass-word-123")
        ChatIA.objects.create(user=user, name="Sofía", email="ana@example.com")
        PerfumeOlfactoryProfile.objects.create(email="ana@example.com", user=user, primary_family="floral")
        erase_linked_user(user)
        self.assertFalse(ChatIA.objects.filter(email="ana@example.com").exists())
        self.assertFalse(PerfumeOlfactoryProfile.objects.filter(email="ana@example.com").exists())
