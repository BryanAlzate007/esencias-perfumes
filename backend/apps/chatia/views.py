from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ChatSerializer
from .services.gemini import GeminiService


class ChatView(APIView):

    def post(self, request):
        serializer = ChatSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = serializer.validated_data["message"]

        try:
            gemini = GeminiService()

            response = gemini.generate_response(message)

            return Response(
                {
                    "response": response,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "error": "No fue posible obtener una respuesta de la IA."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )