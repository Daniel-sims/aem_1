from django.contrib.auth.models import User
from django.db import models
from django.db.models.manager import BaseManager


class CompanyQuerySet(models.QuerySet):
    def active_and_not_deleted(self):
        return self.filter(is_deleted=False, is_active=True)


class CompanyManager(models.Manager):

    def get_queryset(self):
        return CompanyQuerySet(self.model, using=self._db).active_and_not_deleted()

    def create_company(self, company_id, name):
        print(company_id)
        company = Company(company_id=company_id, name=name)
        company.save()

        return company


class Company(models.Model):
    company_id = models.CharField(primary_key=True, max_length=256, null=False, unique=True)
    name = models.CharField(max_length=100, blank=False, null=False)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    objects = CompanyManager()

    def __str__(self):
        return self.name
