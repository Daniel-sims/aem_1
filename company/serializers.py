from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company

        fields = ['company_id', 'name']

    def create_company(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return Company.objects.create_company(**validated_data)
