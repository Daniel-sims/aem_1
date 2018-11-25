from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('client_id', 'name', 'customer_count', 'fully_comp_count', 'basic_cover_count')
