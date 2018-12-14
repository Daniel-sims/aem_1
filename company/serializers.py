from sqlite3 import IntegrityError

from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from aemauthentication.models import User
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    super_user_username = serializers.CharField(min_length=5, max_length=30, write_only=True)
    super_user_password = serializers.CharField(min_length=8, max_length=256, write_only=True)
    super_user_email = serializers.CharField(min_length=8, max_length=256, write_only=True)

    company_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = ['company_id', 'name', 'super_user_username', 'super_user_password', 'super_user_email']

    def validate(self, attrs):
        is_valid = super().validate(attrs)

        if is_valid:
            try:
                User.objects.get(username=attrs['super_user_username'])
            except User.DoesNotExist:
                return super().validate(attrs)

            raise serializers.ValidationError("User already exists.")

    def create(self, validated_data):
        return Company.objects.create_company(**validated_data)
