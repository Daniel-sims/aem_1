import uuid

from rest_framework import serializers
from django.contrib.auth import authenticate

from company.models import Company
from company.serializers import CompanySerializer
from groups.models import AemGroup
from .models import User
from django.contrib.auth.models import Group


class UserSerializer(serializers.ModelSerializer):
    """
    Creates a new User account
    """
    aem_group = serializers.SlugRelatedField(
        queryset=Group.objects.all(),
        slug_field='aemgroup__slug_field',
        write_only=True
    )

    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['company', 'email', 'username', 'password', 'aem_group', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data, company=self.company)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    company_id = serializers.CharField(max_length=255, write_only=True, required=False)

    token = serializers.CharField(max_length=255, read_only=True)

    company_name = serializers.CharField(max_length=255, read_only=True)
    company_pk = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'company_id', 'token', 'first_name', 'last_name', 'role', 'company_name',
                  'company_pk']

    def validate(self, data):
        user = authenticate(username=data.get('username', None), password=data.get('password', None))

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if user.company is None:
            return {
                'token': user.token
            }
        else:
            return {
                'token': user.token,
                'company_name': user.company.name,
                'company_pk': user.company.pk,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
