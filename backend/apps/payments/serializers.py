from rest_framework import serializers

from .wompi import TRANSACTION_ID


class PaymentSessionSerializer(serializers.Serializer):
    order = serializers.IntegerField(required=False, min_value=1)


class PaymentSyncSerializer(serializers.Serializer):
    transaction_id = serializers.RegexField(TRANSACTION_ID.pattern)
