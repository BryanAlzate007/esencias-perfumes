from rest_framework import serializers


class ChatSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, allow_blank=False, max_length=2000)
    chat_id = serializers.UUIDField(required=False, allow_null=True)
    advisor = serializers.CharField(required=False, allow_blank=True, max_length=80)
    language = serializers.CharField(required=False, allow_blank=True, max_length=8)
