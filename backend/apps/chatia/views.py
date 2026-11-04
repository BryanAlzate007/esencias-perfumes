import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChatSerializer
from .services.advisor import UnknownChat, handle_message
from .services.olfactory import language_code, missing_chat_text

logger = logging.getLogger(__name__)


class ChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        language = language_code(serializer.validated_data.get("language"))
        user = request.user if getattr(request.user, "is_authenticated", False) else None
        try:
            result = handle_message(
                chat_id=serializer.validated_data.get("chat_id"),
                message=serializer.validated_data["message"],
                advisor=serializer.validated_data.get("advisor", ""),
                language=language,
                user=user,
            )
        except UnknownChat:
            return Response({"error": missing_chat_text(language)}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception("No fue posible continuar la asesoría.")
            return Response(
                {"error": "No fue posible obtener una respuesta de la IA."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(result, status=status.HTTP_200_OK)
