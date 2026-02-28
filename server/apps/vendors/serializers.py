from rest_framework import serializers
from .models import VendorsStall

class VendorStallSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorsStall
        fields = ['id', 'vendor', 'name', 'description', 'is_open', 'logo', 'banner', 'created_at']
        read_only_fields = ['id', 'created_at', "is_open"] 