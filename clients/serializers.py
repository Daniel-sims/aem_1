from rest_framework import serializers

from company.models import Company
from customers.serializers import CustomerSerializer
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, write_only=True)
    customer = CustomerSerializer(many=True, required=False)

    class Meta:
        model = Client
        fields = ('id', 'company', 'name', 'account_number', 'mobile_number',
                  'landline_number', 'email', 'description', 'system_details', 'customer')

    def create(self, validated_data):
        return Client.objects.create_client(**validated_data, company=self.company)
