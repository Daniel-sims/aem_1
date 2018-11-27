from django.contrib.auth.models import User
from django.db import models


class Company(models.Model):
    company_id = models.CharField(max_length=256, null=False, unique=True)
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.company_id + '-' + self.name

    def create_company(self, company_id, name):
        if company_id is None:
            raise TypeError('Company must have a Company Id.')

        if name is None:
            raise TypeError('Company must have a Name.')

        company = Company(company_id=company_id, name=name)
        company.save()

        return company
