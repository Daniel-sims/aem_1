from django.db import models
import uuid


class ClientQuerySet(models.QuerySet):
    def active_and_not_deleted(self):
        return self.filter(is_deleted=False)


class ClientManager(models.Manager):

    def get_queryset(self):
        return ClientQuerySet(self.model, using=self._db).active_and_not_deleted()

    def create_client(self, company, name, account_number, mobile_number,
                      landline_number, email, description, system_details):
        client = self.model(
            name=name,
            account_number=account_number,
            company=company,
            mobile_number=mobile_number,
            landline_number=landline_number,
            email=email,
            description=description,
            system_details=system_details)
        client.save()

        return client


class Client(models.Model):
    client_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The company which this user is associated with.
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, null=False, blank=False,
                                related_name='client')

    # Company Name
    name = models.CharField(max_length=100, blank=False, null=False)

    # Company Account Number
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

    objects = ClientManager()

    def __str__(self):
        return self.name
