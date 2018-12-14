import factory

from clients.models import Client
from company.factories import CompanyFactory


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    name = factory.Faker('name')
    account_number = factory.Faker('name')

