import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from aemauthentication.factories import AemGroupFactory, UserFactory
from django.conf import settings

from aemauthentication.models import User
from clients.models import Client
from company.factories import CompanyFactory


class CreateClientTestCase(APITestCase):
    valid_client_request_data = {
        "name": "New Client Name",
        "account_number": "W/A123112328",
        "mobile_number": "0191 2131247",
        "landline_number": "07949887097",
        "email": "NewClientEmail@email.com",
        "description": "Description about New Client goes here",
        "system_details": "Details about New Client systems goes here"
    }

    def setUp(self):
        self.aem_admin = UserFactory.create(group=AemGroupFactory.create(
            slug_field=settings.AEM_ADMIN_SLUG_FIELD,
            linked_group__name=settings.AEM_ADMIN_LINKED_GROUP_NAME,
            can_add_permission_slugs=settings.AEM_ADMIN_CAN_ADD_USER_PERMISSIONS,
            client_permissions=settings.AEM_ADMIN_CLIENT_PERMISSIONS,
            customer_permissions=settings.AEM_ADMIN_CUSTOMER_PERMISSIONS,
            company_permissions=settings.AEM_ADMIN_COMPANY_PERMISSIONS
        ))

        self.aem_employee = UserFactory.create(group=AemGroupFactory.create(
            slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD,
            linked_group__name=settings.AEM_EMPLOYEE_LINKED_GROUP_NAME,
            can_add_permission_slugs=settings.AEM_EMPLOYEE_CAN_ADD_USER_PERMISSIONS,
            client_permissions=settings.AEM_EMPLOYEE_CLIENT_PERMISSIONS,
            customer_permissions=settings.AEM_EMPLOYEE_CUSTOMER_PERMISSIONS,
            company_permissions=settings.AEM_EMPLOYEE_COMPANY_PERMISSIONS
        ))

        client_company = CompanyFactory.create()

        self.aem_customer_super_user = UserFactory.create(
            company=client_company,
            group=AemGroupFactory.create(
                slug_field=settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
                linked_group__name=settings.AEM_CUSTOMER_SUPER_USER_LINKED_GROUP_NAME,
                can_add_permission_slugs=settings.AEM_CUSTOMER_SUPER_USER_CAN_ADD_USER_PERMISSIONS,
                client_permissions=settings.AEM_CUSTOMER_SUPER_USER_CLIENT_PERMISSIONS,
                customer_permissions=settings.AEM_CUSTOMER_SUPER_USER_CUSTOMER_PERMISSIONS,
                company_permissions=settings.AEM_CUSTOMER_SUPER_USER_COMPANY_PERMISSIONS
            )
        )

        self.aem_customer_admin = UserFactory.create(
            company=client_company,
            group=AemGroupFactory.create(
                slug_field=settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
                linked_group__name=settings.AEM_CUSTOMER_ADMIN_LINKED_GROUP_NAME,
                can_add_permission_slugs=settings.AEM_CUSTOMER_ADMIN_CAN_ADD_USER_PERMISSIONS,
                client_permissions=settings.AEM_CUSTOMER_ADMIN_CLIENT_PERMISSIONS,
                customer_permissions=settings.AEM_CUSTOMER_ADMIN_CUSTOMER_PERMISSIONS,
                company_permissions=settings.AEM_CUSTOMER_ADMIN_COMPANY_PERMISSIONS
            )
        )

        self.aem_customer_user = UserFactory.create(
            company=client_company,
            group=AemGroupFactory.create(
                slug_field=settings.AEM_CUSTOMER_USER_SLUG_FIELD,
                linked_group__name=settings.AEM_CUSTOMER_USER_LINKED_GROUP_NAME,
                can_add_permission_slugs=settings.AEM_CUSTOMER_USER_CAN_ADD_USER_PERMISSIONS,
                client_permissions=settings.AEM_CUSTOMER_USER_CLIENT_PERMISSIONS,
                customer_permissions=settings.AEM_CUSTOMER_USER_CUSTOMER_PERMISSIONS,
                company_permissions=settings.AEM_CUSTOMER_USER_COMPANY_PERMISSIONS
            )
        )

    def _test_list_create_client_view_permission(self, user, data, expected_status_code, response_keys=None):
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('list-create-client'), data, format='json')

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if response_keys:
            for key in response_keys:
                response_field = response.json()[key]
                self.assertIsNotNone(response_field)

    def test_aem_admin_cant_create_client(self):
        self._test_list_create_client_view_permission(user=self.aem_admin,
                                                      data=self.valid_client_request_data,
                                                      expected_status_code=status.HTTP_403_FORBIDDEN,
                                                      response_keys=('detail',))

    def test_aem_employee_cant_create_client(self):
        self._test_list_create_client_view_permission(user=self.aem_employee,
                                                      data=self.valid_client_request_data,
                                                      expected_status_code=status.HTTP_403_FORBIDDEN,
                                                      response_keys=('detail',))

    def test_aem_customer_super_user_can_create_client(self):
        self._test_list_create_client_view_permission(user=self.aem_customer_super_user,
                                                      data=self.valid_client_request_data,
                                                      expected_status_code=status.HTTP_201_CREATED,
                                                      response_keys=(
                                                          'name', 'account_number', 'mobile_number', 'landline_number',
                                                          'email', 'description',
                                                          'system_details'))

        new_client = Client.objects.get(name=self.valid_client_request_data['name'])
        self.assertIsNotNone(new_client)
        self.assertEqual(new_client.company.id, self.aem_customer_super_user.company.id)

    def test_aem_customer_customer_admin_can_create_client(self):
        user = self.aem_customer_super_user
        self._test_list_create_client_view_permission(user=user,
                                                      data=self.valid_client_request_data,
                                                      expected_status_code=status.HTTP_201_CREATED,
                                                      response_keys=(
                                                          'name', 'account_number', 'mobile_number', 'landline_number',
                                                          'email', 'description',
                                                          'system_details'))

        new_client = Client.objects.get(name=self.valid_client_request_data['name'])
        self.assertIsNotNone(new_client)
        self.assertEqual(new_client.company.id, self.aem_customer_super_user.company.id)

    def test_aem_customer_user_cant_create_client(self):
        self._test_list_create_client_view_permission(user=self.aem_employee,
                                                      data=self.valid_client_request_data,
                                                      expected_status_code=status.HTTP_403_FORBIDDEN,
                                                      response_keys=('detail',))
