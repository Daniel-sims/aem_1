from rest_framework import serializers

from clients.models import Client
from company.models import Company
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, write_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False, write_only=True)

    class Meta:
        model = Customer
        fields = ('customer_id', 'company', 'client', 'name', 'account_number', 'mobile_number',
                  'landline_number', 'email', 'description', 'system_details')

    def create(self, validated_data):
        return Customer.objects.create_customer(**validated_data, company=self.company)
