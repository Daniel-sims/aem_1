import uuid

from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Creates a new default User associated with the Company.
    """
    class Meta:
        model = User
        fields = ['company', 'email', 'username', 'password', 'token']
        read_only_fields = ['token']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    company_id = serializers.CharField(max_length=255, write_only=True, required=False)

    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        print(data)

        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        return {
            'token': user.token
        }
