from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView

from clients.models import Client
from clients.serializers import ClientSerializer
from rest_framework import generics, permissions, status


class CanCreateClientPermission(BasePermission):
    message = "Invalid permissions to create customer."

    def has_permission(self, request, view):
        if not request.user.company:
            self.message = 'You must be associated with a company to create a client.'
            return False

        return True


class CreateClientAPIView(ListCreateAPIView):
    """
    Creates a new Client.
    """
    permission_classes = (IsAuthenticated, CanCreateClientPermission, )
    serializer_class = ClientSerializer

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        serializer.company = self.request.user.company
        return serializer

    def get_queryset(self):
        return Client.objects.filter(company__user=self.request.user)
