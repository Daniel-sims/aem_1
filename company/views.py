from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company
from company.serializers import CompanySerializer


class OnlyAEMPermission(permissions.BasePermission):
    message = 'Requires AEM Admin permission.'

    def has_permission(self, request, view):
        return self.request.user.has_perm('aem_admin')


class CreateCompanyAPIView(APIView):
    permission_classes = (IsAuthenticated, permissions.DjangoModelPermissions)
    serializer_class = CompanySerializer
    queryset = Company.objects.get_queryset()

    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            print('is valid')
            print(serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
