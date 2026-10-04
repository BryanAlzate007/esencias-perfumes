from django.conf import settings
from google import genai


class GeminiService:
    MODEL = "gemini-3.5-flash-lite"

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_response(self, message: str) -> str:
        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=message,
        )

        return response.text