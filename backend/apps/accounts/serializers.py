from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.core.permissions import is_admin_user, user_role

from .models import Profile

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    country = serializers.CharField(source="profile.country", required=False, allow_blank=True)
    phone = serializers.CharField(source="profile.phone", required=False, allow_blank=True)
    whatsapp = serializers.CharField(source="profile.whatsapp", required=False, allow_blank=True)
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "country",
            "phone",
            "whatsapp",
            "role",
            "is_admin",
        )
        read_only_fields = ("id", "username", "email", "role", "is_admin")

    def get_role(self, obj):
        return user_role(obj)

    def get_is_admin(self, obj):
        return is_admin_user(obj)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.save()
        profile, _ = Profile.objects.get_or_create(user=instance)
        updated = []
        for field in ("country", "phone", "whatsapp"):
            if field in profile_data:
                setattr(profile, field, profile_data[field])
                updated.append(field)
        if updated:
            profile.save(update_fields=updated)
        return instance


class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.Role.choices, required=False)
    country = serializers.CharField(source="profile.country", read_only=True)
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "country",
            "role",
            "is_admin",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("id", "username", "email", "country", "date_joined", "is_admin")

    def get_is_admin(self, obj):
        return is_admin_user(obj)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["role"] = user_role(instance)
        return data

    def update(self, instance, validated_data):
        role = validated_data.pop("role", None)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        if role:
            instance.is_staff = role == Profile.Role.ADMIN
            profile, _ = Profile.objects.get_or_create(user=instance)
            profile.role = role
            profile.save(update_fields=["role"])
        instance.save()
        return instance
