from rest_framework import serializers

from clients.models import Client
from company.models import Company
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False, write_only=True)

    class Meta:
        model = Customer
        fields = ('id', 'client', 'name', 'account_number', 'mobile_number',
                  'landline_number', 'email', 'description', 'system_details')

    def create(self, validated_data):
        return Customer.objects.create_customer(**validated_data)
