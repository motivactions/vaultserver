from rest_framework import serializers

from ...models import Entry, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class EntrySerializer(serializers.ModelSerializer):
    trx = TransactionSerializer()
    amount = serializers.FloatField()
    computed_amount = serializers.FloatField()

    class Meta:
        model = Entry
        fields = "__all__"
