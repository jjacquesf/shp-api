from rest_framework import serializers

from core.serializers import (
    IntegerListField,
)

class EvidenceReportSerializer(serializers.Serializer):
    """Serializer for user group update."""
    group_id = serializers.IntegerField(required=True)
    type_id = serializers.IntegerField(required=True)
    division_id = serializers.IntegerField(required=True)
    cf_ids = IntegerListField()
    from_date = serializers.DateField(format="%Y-%m-%d", required=False)
    to_date = serializers.DateField(format="%Y-%m-%d", required=False)
