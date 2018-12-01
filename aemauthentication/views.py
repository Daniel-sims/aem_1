from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    RegistrationSerializer,
    LoginSerializer, UserTypeSerializer)


class RegistrationAPIView(APIView):
    """
    View for Registering a AEM Customer Admin account.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserAPIView(RegistrationAPIView):
    """
    View for Registering an AEM Customer Engineer account.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserTypeSerializer


class LoginAPIView(APIView):
    """
    View for authenticating all Users.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
