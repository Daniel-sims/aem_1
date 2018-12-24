from django.conf import settings
from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company, CompanyModule
from company.serializers import CompanySerializer


class CanListCreateCompanyPermission(BasePermission):
    message = "Invalid permissions."

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm(settings.VIEW_COMPANY_PERMISSION)
        elif request.method == 'POST':
            return request.user.has_perm(settings.ADD_COMPANY_PERMISSION)

        return False


class ListCreateCompanyAPIView(ListCreateAPIView):
    """
    Lists or creates companies.
    """
    permission_classes = (IsAuthenticated, CanListCreateCompanyPermission)
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class CanRetrieveCompanyPermission(BasePermission):
    message = "Invalid permissions."

    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.groups.filter(name__in=['AEM Admin', 'AEM Employee']) or request.user.is_superuser:
                return True
            elif request.user.company is not None:
                print(request.user.company.pk)
                print(view.kwargs.get('pk', None))
                if request.user.company.pk is view.kwargs.get('pk', None):
                    return True
                else:
                    return request.user.has_perm(settings.VIEW_COMPANY_PERMISSION)

        return True


class RetrieveCompanyAPIView(RetrieveAPIView):
    """
    Retriecves a company based on PK
    """
    permission_classes = (IsAuthenticated, CanRetrieveCompanyPermission)
    serializer_class = CompanySerializer

    def get_object(self):
        return get_object_or_404(Company.objects.filter(pk=self.kwargs['pk']))


