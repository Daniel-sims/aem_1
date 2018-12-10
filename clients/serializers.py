from rest_framework import serializers

from company.models import Company
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False)

    class Meta:
        model = Client
        fields = ('company', 'name', 'account_number', 'mobile_number',
                  'landline_number', 'email', 'description', 'system_details')

    def create(self, validated_data):
        return Client.objects.create_client(**validated_data, company=self.company)
