from django.db import models
import uuid


class CustomerQuerySet(models.QuerySet):
    def active_and_not_deleted(self):
        return self.filter(is_deleted=False)


class CustomerManager(models.Manager):

    def get_queryset(self):
        return CustomerQuerySet(self.model, using=self._db).active_and_not_deleted()

    def create_customer(self, client, name, account_number, mobile_number,
                        landline_number, email, description, system_details):
        customer = self.model(
            client=client,
            name=name,
            account_number=account_number,
            mobile_number=mobile_number,
            landline_number=landline_number,
            email=email,
            description=description,
            system_details=system_details)
        customer.save()

        return customer


class Customer(models.Model):
    # Client which this Customer belongs to
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, null=False, blank=False,
                               related_name='customer')

    # Customer Name
    name = models.CharField(max_length=100, blank=False, null=False)

    # Account Number
    account_number = models.CharField(max_length=16, default=0, blank=False, null=False)

    # Mobile Number
    mobile_number = models.CharField(max_length=14, blank=True, null=True)

    # Landline Number
    landline_number = models.CharField(max_length=14, blank=True, null=True)

    # Description
    description = models.CharField(max_length=256, blank=True, null=True)

    # System Details
    system_details = models.CharField(max_length=256, blank=True, null=True)

    # Email
    email = models.EmailField()

    # Indicates whether this user has been deleted or not
    is_deleted = models.BooleanField(default=False)

    objects = CustomerManager()

    def __str__(self):
        return self.name
