from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company
from company.serializers import CompanySerializer


class CanCreateCompanyPermission(BasePermission):
    """

    """
    message = "Invalid permissions to create a company."

    def has_permission(self, request, view):
        return request.user.has_perm('Can add company')


class CreateCompanyAPIView(APIView):
    """
    Creates a new Company.
    """
    permission_classes = (IsAuthenticated, CanCreateCompanyPermission)
    serializer_class = CompanySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
