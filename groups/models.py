from django.contrib.auth.models import Group
from django.db import models

class GroupQuerySet(models.QuerySet):
    def for_company(self):
        return self.filter()


class GroupManager(models.Manager):

    def get_queryset(self):
        return GroupQuerySet(self.model, using=self._db).for_company()

    def create_group(self):
        pass


class CompanyGroup(Group):
    slug_field = models.SlugField()
    company_id = models.CharField(max_length=256, null=False)

    objects = GroupManager()

    def __str__(self):
        return self.slug_field
