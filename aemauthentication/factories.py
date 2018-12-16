import factory
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from factory import lazy_attribute
from faker import Faker

from aemauthentication.models import User
from clients.models import Client
from company.models import Company
from customers.models import Customer
from groups.models import AemGroup

FAKER = Faker(locale='en_US')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = lazy_attribute(lambda x: FAKER.name())
    password = 'Password01'
    email = lazy_attribute(lambda a: '{0}@example.com'.format(a.username).lower())

    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.groups.add(extracted.linked_group)


class GroupsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = ""


class AemGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AemGroup

    linked_group = factory.SubFactory(GroupsFactory)
    slug_field = ""

    @factory.post_generation
    def can_add_permission_slugs(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for slug in extracted:
                self.linked_group.permissions.add(Permission.objects.get_or_create(
                    name='Can add {}'.format(slug),
                    content_type=ContentType.objects.get_for_model(AemGroup),
                    codename='can_add_{}'.format(slug)
                )[0])

    @factory.post_generation
    def client_permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            all_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Client))
            for perm in extracted:
                # This when using has_perm you need the object type before, i.e client.add_client.
                # but when looking for these permissions you only need add_client.
                # to avoid multiple definitions of the same thing just split the string from the .
                sanitized_perm_name = perm.split(".", 1)[1]
                for p in all_permissions:
                    if p.codename == sanitized_perm_name:
                        self.linked_group.permissions.add(p)

    @factory.post_generation
    def company_permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            all_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Company))
            for perm in extracted:
                # This when using has_perm you need the object type before, i.e client.add_client.
                # but when looking for these permissions you only need add_client.
                # to avoid multiple definitions of the same thing just split the string from the .
                sanitized_perm_name = perm.split(".", 1)[1]
                for p in all_permissions:
                    if p.codename == sanitized_perm_name:
                        self.linked_group.permissions.add(p)

    @factory.post_generation
    def customer_permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            all_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Customer))
            for perm in extracted:
                # This when using has_perm you need the object type before, i.e client.add_client.
                # but when looking for these permissions you only need add_client.
                # to avoid multiple definitions of the same thing just split the string from the .
                sanitized_perm_name = perm.split(".", 1)[1]
                for p in all_permissions:
                    if p.codename == sanitized_perm_name:
                        self.linked_group.permissions.add(p)
