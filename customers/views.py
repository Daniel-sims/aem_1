import itertools

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

        return True


class CreateCustomerAPIView(ListCreateAPIView):
    """
    Creates a new Customer.
    """
    permission_classes = (IsAuthenticated, CanCreateCustomerPermission, )
    serializer_class = CustomerSerializer

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        serializer.company = self.request.user.company
        return serializer

    def get_queryset(self):
        return Customer.objects.filter(company__user=self.request.user)
