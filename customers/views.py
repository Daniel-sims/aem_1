import itertools

from django.conf import settings
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView

from clients.models import Client
from clients.serializers import ClientSerializer
from rest_framework import generics, permissions, status

from customers.models import Customer
from customers.serializers import CustomerSerializer


class CanCreateCustomerPermission(BasePermission):
    message = "Invalid permissions to create customer."

    def has_permission(self, request, view):
        if not request.user.company:
            self.message = 'You must be associated with a company to create a customer.'
            return False

        if not request.user.has_perm(settings.ADD_CUSTOMER_PERMISSION):
            self.message = 'Invalid permissions to create a customer.'
            return False

        try:
            client = Client.objects.get(id=request.data['client'])

            if client.company.id != request.user.company.id:
                self.message = 'Client does not belong to your company.'
                return False
        except Client.DoesNotExist:
            self.message = 'Client does not exist.'
            return False

        return True


class CreateCustomerAPIView(ListCreateAPIView):
    """
    Creates a new Customer.
    """
    permission_classes = (IsAuthenticated, CanCreateCustomerPermission,)
    serializer_class = CustomerSerializer

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        serializer.company = self.request.user.company
        return serializer

    def get_queryset(self):
        return Customer.objects.filter(company__user=self.request.user)
