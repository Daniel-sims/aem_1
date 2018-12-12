import uuid

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
            ),
            client_permissions=(
                'Can add client',
            )
        )

        self.aem_customer_admin_group = AemGroupFactory.create(
            slug_field=settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            linked_group__name="Aem Customer Admin",
            can_add_permission_slugs=(
                settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            ),
            client_permissions=(
                'Can add client',
            )
        )

        self.aem_customer_user_group = AemGroupFactory.create(
            slug_field=settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            linked_group__name="Aem Customer User",
            can_add_permission_slugs=())

    def _test_permission(self, user, data, expected_status_code, response_contains_kvp=None):
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('list-create-client'), data, format='json')

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if response_contains_kvp:
            for kvp in response_contains_kvp:
                response_field = response.json()[kvp[0]]
                self.assertIsNotNone(response_field)
                if kvp[1]:
                    self.assertTrue(kvp[1], response_field)

    def test_aem_admin_cant_create_client(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))

        self._test_permission(user=user, data={
            "name": "newClient",
            "account_number": "AN12345678"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'You must be associated with a company to create a client.'),
                              ))

    def test_aem_employee_cant_create_client(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))

        self._test_permission(user=user, data={
            "name": "newClient",
            "account_number": "AN12345678"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'You must be associated with a company to create a client.'),
                              ))

    def test_aem_customer_super_user_can_create_client(self):
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create())

        self._test_permission(user=user, data={
            "name": "New Client Name",
            "account_number": "W/A123112328",
            "mobile_number": "0191 2131247",
            "landline_number": "07949887097",
            "email": "NewClientEmail@email.com",
            "description": "Description about New Client goes here",
            "system_details": "Details about New Client systems goes here"
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('name', 'New Client Name'),
                                  ('account_number', 'W/A123112328'),
                                  ('mobile_number', '0191 2131247'),
                                  ('landline_number', '07949887097'),
                                  ('email', 'NewClientEmail@email.com'),
                                  ('description', 'Description about New Client goes here'),
                                  ('system_details', 'Details about New Client systems goes here'),
                              ))

        self.assertIsNotNone(user.company.client.all())
        self.assertEqual(len(user.company.client.all()), 1)
        self.assertTrue(user.company.client.filter(name='New Client Name').exists())

    def test_aem_customer_customer_admin_can_create_client(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create())

        self._test_permission(user=user, data={
            "name": "New Client Name",
            "account_number": "W/A123112328",
            "mobile_number": "0191 2131247",
            "landline_number": "07949887097",
            "email": "NewClientEmail@email.com",
            "description": "Description about New Client goes here",
            "system_details": "Details about New Client systems goes here"
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('name', 'New Client Name'),
                                  ('account_number', 'W/A123112328'),
                                  ('mobile_number', '0191 2131247'),
                                  ('landline_number', '07949887097'),
                                  ('email', 'NewClientEmail@email.com'),
                                  ('description', 'Description about New Client goes here'),
                                  ('system_details', 'Details about New Client systems goes here'),
                              ))

        self.assertIsNotNone(user.company.client.all())
        self.assertEqual(len(user.company.client.all()), 1)
        self.assertTrue(user.company.client.filter(name='New Client Name').exists())

    def test_aem_customer_user_cant_create_client(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create())

        self._test_permission(user=user, data={
            "name": "New Client Name",
            "account_number": "W/A123112328",
            "mobile_number": "0191 2131247",
            "landline_number": "07949887097",
            "email": "NewClientEmail@email.com",
            "description": "Description about New Client goes here",
            "system_details": "Details about New Client systems goes here"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create Client.'),))


    def test_aem_customer_admin_cant_create_client_for_other_company(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create())

        self._test_permission(user=user, data={
            "name": "New Client Name",
            "account_number": "W/A123112328",
            "mobile_number": "0191 2131247",
            "landline_number": "07949887097",
            "email": "NewClientEmail@email.com",
            "description": "Description about New Client goes here",
            "system_details": "Details about New Client systems goes here"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create Client.'),))
