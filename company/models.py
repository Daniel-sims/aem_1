import uuid

from django.db import models, transaction
from django.db.models.manager import BaseManager

from aemauthentication.models import User
from groups.models import AemGroup


class CompanyQuerySet(models.QuerySet):
    def active_and_not_deleted(self):
        return self.filter(is_deleted=False, is_active=True)


class CompanyManager(models.Manager):

    def get_queryset(self):
        return CompanyQuerySet(self.model, using=self._db).active_and_not_deleted()

    def create_company(self, name, super_user_username, super_user_password, super_user_email):
        company = self.model(company_id=uuid.uuid4(), name=name)

        with transaction.atomic():
            company.save()

            User.objects.create_user(
                username=super_user_username,
                password=super_user_password,
                email=super_user_email,
                company=company,
                aem_group=AemGroup.objects.filter(slug_field='aem-customer-super-user').first().linked_group
            )

        return company


class Company(models.Model):
    company_id = models.UUIDField(primary_key=True, max_length=256, null=False, unique=True)
    name = models.CharField(max_length=100, blank=False, null=False)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    objects = CompanyManager()

    def __str__(self):
        return self.name
