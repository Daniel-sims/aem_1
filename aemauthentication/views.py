from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from .serializers import (
    LoginSerializer,
    UserSerializer)


class CanCreateUserGroupPermission(BasePermission):
    message = "Invalid permissions to create customer."

    def has_permission(self, request, view):
        if not request.user.has_perm('groups.can_add_{}'.format(request.data.get('aem_group'))):
            self.message = "Invalid permissions to create this account type."
            return False

        if not request.user.company:
            request_user_is_staff = request.user.is_superuser \
                                    or request.user.groups.filter(
                aemgroup__slug_field=settings.AEM_SUPER_USER_SLUG_FIELD).exists() \
                                    or request.user.groups.filter(
                aemgroup__slug_field=settings.AEM_ADMIN_SLUG_FIELD).exists() \
                                    or request.user.groups.filter(
                aemgroup__slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD).exists()

            if not request_user_is_staff:
                self.message = "Invalid account type, user doesn't belong to a company but is not an AEM Staff account."
                return False
            else:
                new_user_group = request.data.get('aem_group')
                if not new_user_group == settings.AEM_ADMIN_SLUG_FIELD \
                        or not new_user_group == settings.AEM_EMPLOYEE_SLUG_FIELD:
                    self.message = "You must be associated with a company to create a new user that is not an AEM Staff account."

        return True


class CreateUserAPIView(CreateAPIView):
    """
    Creates a new User Account.
    """
    permission_classes = (IsAuthenticated, CanCreateUserGroupPermission)
    serializer_class = UserSerializer

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        serializer.company = self.request.user.company

        return serializer


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
