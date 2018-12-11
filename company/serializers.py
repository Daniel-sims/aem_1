from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    super_user_username = serializers.CharField(min_length=5, max_length=30, write_only=True)
    super_user_password = serializers.CharField(min_length=8, max_length=256, write_only=True)
    super_user_email = serializers.CharField(min_length=8, max_length=256, write_only=True)

    company_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Company
        fields = ['company_id', 'name', 'super_user_username', 'super_user_password', 'super_user_email']

    def create(self, validated_data):
        return Company.objects.create_company(**validated_data)
