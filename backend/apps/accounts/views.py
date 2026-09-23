from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole

from .models import Profile_person
from .serializers import AdminUserSerializer, MeSerializer, ProfilePersonSerializer

User = get_user_model()


class ProfilePersonViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilePersonSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = Profile_person.objects.all()
    pagination_class = None


class CsrfCookieView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"detail": "ok"})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = User.objects.select_related("profile").order_by("-date_joined")


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = User.objects.select_related("profile")
