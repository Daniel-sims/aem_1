from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from aemauthentication.factories import AemGroupFactory, UserFactory
from django.conf import settings

from company.factories import CompanyFactory


class CreateClientTestCase(APITestCase):

    def setUp(self):
        self.aem_admin_group = AemGroupFactory.create(
            slug_field=settings.AEM_ADMIN_SLUG_FIELD,
            linked_group__name="Aem Admin",
            can_add_permission_slugs=(
                settings.AEM_EMPLOYEE_SLUG_FIELD,
            )
        )

        self.aem_employee_group = AemGroupFactory.create(
            slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD,
            linked_group__name="Aem Employee",
            can_add_permission_slugs=()
        )

        self.aem_customer_super_user_group = AemGroupFactory.create(
            slug_field=settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
            linked_group__name="Aem Customer Super Admin",
            can_add_permission_slugs=(
                settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
                settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
        )

        self.aem_customer_admin_group = AemGroupFactory.create(
            slug_field=settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            linked_group__name="Aem Customer Admin",
            can_add_permission_slugs=(
                settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
        )

        self.aem_customer_user_group = AemGroupFactory.create(
            slug_field=settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            linked_group__name="Aem Customer User",
            can_add_permission_slugs=())

    def _test_permission(self, user, data, expected_status_code, expected_detail_message=None):
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('create-client'), data)

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if expected_detail_message:
            self.assertEqual(response.content, expected_detail_message)

    def test_aem_admin_cant_create_client(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))

        self._test_permission(user=user, data={
            "name": "newClient",
            "account_number": "AN12345678"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"You must be associated with a company to create a client."}')

    def test_aem_employee_cant_create_client(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))

        self._test_permission(user=user, data={
            "name": "newClient",
            "account_number": "AN12345678"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"You must be associated with a company to create a client."}')

    def test_aem_customer_super_user_can_create_client(self):
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "name": "newClient",
            "account_number": "AN12345678"
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"name":"newClient","account_number":"AN12345678","company":"users-company-id"}')

        self.assertIsNotNone(user.company.client.all())
        self.assertEqual(len(user.company.client.all()), 1)
        self.assertIsNotNone(user.company.client.filter(name='newClient'))
        self.assertIsNotNone(user.company.client.filter(account_number='AN12345678'))

    def test_aem_customer_customer_admin_can_create_client(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "name": "newClient",
            "account_number": "AN12345678"
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"name":"newClient","account_number":"AN12345678","company":"users-company-id"}')

        self.assertIsNotNone(user.company.client.all())
        self.assertEqual(len(user.company.client.all()), 1)
        self.assertIsNotNone(user.company.client.filter(name='newClient'))
        self.assertIsNotNone(user.company.client.filter(account_number='AN12345678'))

    def test_aem_customer__user_can_create_client(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "name": "newClient",
            "account_number": "AN12345678"
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"name":"newClient","account_number":"AN12345678","company":"users-company-id"}')

        self.assertIsNotNone(user.company.client.all())
        self.assertEqual(len(user.company.client.all()), 1)
        self.assertIsNotNone(user.company.client.filter(name='newClient'))
        self.assertIsNotNone(user.company.client.filter(account_number='AN12345678'))
