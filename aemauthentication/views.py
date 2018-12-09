from rest_framework import status
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
        user_is_customer = request.user.groups.filter(
            aemgroup__slug_field=settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD).exists() \
                           or request.user.groups.filter(
            aemgroup__slug_field=settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD).exists() \
                           or request.user.groups.filter(
            aemgroup__slug_field=settings.AEM_CUSTOMER_USER_SLUG_FIELD).exists()

        # If the user group of the new user is to be an AEM Staff account, make sure they're not trying to assign
        # this to a company.
        new_user_group = request.data.get('aem_group')
        if new_user_group == settings.AEM_ADMIN_SLUG_FIELD or new_user_group == settings.AEM_EMPLOYEE_SLUG_FIELD:
            if request.data.get('company'):
                self.message = "A AEM Admin or AEM Employee account cannot be associated with a company."
                return False

        # If the user is a customer they can only assign users to the same company as them
        if user_is_customer:
            user_company = request.user.company

            if not user_company:
                # This should only happen if their account has been manually fucked up
                self.message = "Debug - User is a customer but is not in a company."
                return False

            new_user_is_in_users_company = request.user.company.company_id == request.data.get('company')

            if not new_user_is_in_users_company:
                self.message = "Debug - You cannot create a user that is not in your company."
                return False
        else:
            # The user is not part of any of the customer groups
            user_is_aem_staff = request.user.is_superuser or request.user.groups.filter(
                aemgroup__slug_field=settings.AEM_SUPER_USER_SLUG_FIELD).exists() \
                                or request.user.groups.filter(
                aemgroup__slug_field=settings.AEM_ADMIN_SLUG_FIELD).exists() \
                                or request.user.groups.filter(
                aemgroup__slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD).exists()

            if not user_is_aem_staff:
                # Fuck knows how they've managed to get this far and fail
                self.message = "Debug - User is not a customer, but also not a staff member???"
                return False

        user_has_permission_to_create_account_type = request.user.has_perm(
            'groups.can_add_{}'.format(request.data.get('aem_group')))

        if not user_has_permission_to_create_account_type:
            self.message = "Invalid permissions to create this account type."
            return False

        return True


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
