from django.conf import settings
from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company
from company.serializers import CompanySerializer


class CanCreateCompanyPermission(BasePermission):
    message = "Invalid permissions to create a company."

    def has_permission(self, request, view):
        return request.user.has_perm(settings.ADD_COMPANY_PERMISSION)


class ListCreateCompanyAPIView(ListCreateAPIView):
    """
    Creates a new Company.
    """
    permission_classes = (IsAuthenticated, CanCreateCompanyPermission)
    serializer_class = CompanySerializer
