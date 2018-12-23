from django.conf import settings
from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company, CompanyModule
from company.serializers import CompanySerializer


class CanListCreateCompanyPermission(BasePermission):
    message = "Invalid permissions to create a company."

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        elif request.method == 'POST':
            return request.user.has_perm(settings.ADD_COMPANY_PERMISSION)

        return False


class ListCreateCompanyAPIView(ListCreateAPIView):
    """
    Creates a new Company.
    """
    permission_classes = (IsAuthenticated, CanListCreateCompanyPermission)
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company.id)
