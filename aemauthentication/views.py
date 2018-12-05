from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    UserSerializer)


class CanCreateUserGroupPermission(BasePermission):
    """
    Checks to see if the user has the correct permission to create the user.

    If the request is trying to create a user with the "aem-admin" group field, their own permissions list
    must contain the "Can add aem admin" permission.
    """
    message = "Invalid permissions to create user type."

    def has_permission(self, request, view):
        group = request.data.get('aem_group')
        return request.user.has_perm('groups.can_add_{}'.format(group))


class CreateUserAPIView(APIView):
    """
    Creates a new User Account.
    """
    permission_classes = (IsAuthenticated, CanCreateUserGroupPermission)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
