from sqlite3 import IntegrityError

from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from aemauthentication.models import User
from .models import Company, CompanyModule


class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyModule
        fields = ['name', 'slug_field']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']


class CompanySerializer(serializers.ModelSerializer):
    user = UserSerializer(write_only=True)
    modules = ModulesSerializer(many=True)

    company_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = ['company_id', 'name', 'user', 'modules']

    def create(self, validated_data):
        return Company.objects.create_company(**validated_data)
