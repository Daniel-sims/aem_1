from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AemGroupQuerySet(models.QuerySet):
    def for_company(self):
        return self.filter()


class AemGroupManager(models.Manager):

    def get_queryset(self):
        return AemGroupQuerySet(self.model, using=self._db).for_company()


class AemGroup(models.Model):
    linked_group = models.ForeignKey(Group, related_name='aemgroup', on_delete=models.CASCADE)
    slug_field = models.SlugField(unique=True)

    objects = AemGroupManager()

    def __str__(self):
        return self.slug_field

    """
    Override the save method for creating a new CompanyGroup.
    
    When creating a new CompanyGroup, create a new permission for the Group that associates with adding to the group.
    
    I.E if you're creating the group "AEM Admin" with the slug "aem-admin", a permission called "Can add aem admin"
    will be created, which allows you to assign this permission to other groups, so when a user tries to create a user
    with the slugs "aem-admin" they will require the permission "Can add aem admin".
    """
    def save(self, **kwargs):
        # If we're saving a new CompanyGroup
        if not self.id:
            Permission.objects.get_or_create(
                name='Can add {}'.format(self.slug_field),
                content_type=ContentType.objects.get_for_model(AemGroup),
                codename='can_add_{}'.format(self.slug_field)
            )

        super().save(**kwargs)
