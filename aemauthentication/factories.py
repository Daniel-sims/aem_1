import factory
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from aemauthentication.models import User
from clients.models import Client
from company.models import Company
from customers.models import Customer
from groups.models import AemGroup


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('first_name')
    password = 'Password01'
    email = factory.LazyAttribute(lambda a: '{0}@example.com'.format(a.username).lower())

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group.linked_group)


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
                for p in all_permissions:
                    if p.name == perm:
                        self.linked_group.permissions.add(p)

    @factory.post_generation
    def company_permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            all_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Company))
            for perm in extracted:
                for p in all_permissions:
                    if p.name == perm:
                        self.linked_group.permissions.add(p)

    @factory.post_generation
    def customer_permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            all_permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Customer))
            for perm in extracted:
                for p in all_permissions:
                    if p.name == perm:
                        self.linked_group.permissions.add(p)
