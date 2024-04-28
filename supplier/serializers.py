from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from stdnum.mx.rfc import (validate)
# (validate,InvalidComponent,InvalidFormat,InvalidLength,InvalidChecksum)

from core import models


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for the supplier object"""    
    
    class Meta:
        model= models.Supplier
        fields = ['id', 'is_active', 'name', 'tax_id', 'tax_name']
        read_only_fields = ['id']

    def __str__(self):
        return f'Supplier: {self.name}'
    
    def validate_tax_id(self, value):
        if not validate(value):
            raise serializers.ValidationError(_('El RFC no tiene el formato esperado'))

        return value