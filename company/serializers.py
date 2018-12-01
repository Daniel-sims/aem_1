from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company

        fields = ['company_id', 'name']

    def create(self, validated_data):
        print('create company called')
        return Company.objects.create_company(**validated_data)
