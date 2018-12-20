import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from aemauthentication.factories import AemGroupFactory, UserFactory
from django.conf import settings

from clients.factories import ClientFactory
from clients.models import Client
from company.factories import CompanyFactory
from customers.models import Customer


class CreateCustomerTestCase(APITestCase):
    valid_add_customer_request = {
        "client": 0,
        "name": "Some Wonderful Customer",
        "account_number": "W/L141123512",
        "mobile_number": "0191 2131247",
        "landline_number": "07949887097",
        "email": "WonderfulCustomer@email.com",
        "description": "Description about this wonderful customer goes here.",
        "system_details": "System details about this wonderful customers alarms go in here."
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

        client_company_two = CompanyFactory.create()

        self.aem_customer_super_user_company_two = UserFactory.create(
            company=client_company_two,
            group=AemGroupFactory.create(
                slug_field=settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
                linked_group__name=settings.AEM_CUSTOMER_SUPER_USER_LINKED_GROUP_NAME,
                can_add_permission_slugs=settings.AEM_CUSTOMER_SUPER_USER_CAN_ADD_USER_PERMISSIONS,
                client_permissions=settings.AEM_CUSTOMER_SUPER_USER_CLIENT_PERMISSIONS,
                customer_permissions=settings.AEM_CUSTOMER_SUPER_USER_CUSTOMER_PERMISSIONS,
                company_permissions=settings.AEM_CUSTOMER_SUPER_USER_COMPANY_PERMISSIONS
            )
        )

    def _test_list_create_customer_view_permissions(self, user, data, expected_status_code, response_keys=None):
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('list-create-customer'), data, format='json')

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if response_keys:
            for key in response_keys:
                response_field = response.json()[key]
                self.assertIsNotNone(response_field)

    def test_aem_admin_cant_create_customer(self):
        self.valid_add_customer_request['client'] = 1
        self._test_list_create_customer_view_permissions(user=self.aem_admin,
                                                         data=self.valid_add_customer_request,
                                                         expected_status_code=status.HTTP_403_FORBIDDEN,
                                                         response_keys=('detail',))

    def test_aem_employee_cant_create_customer(self):
        self.valid_add_customer_request['client'] = 1
        self._test_list_create_customer_view_permissions(user=self.aem_employee,
                                                         data=self.valid_add_customer_request,
                                                         expected_status_code=status.HTTP_403_FORBIDDEN,
                                                         response_keys=('detail',))

    def test_aem_customer_super_user_can_create_customer(self):
        user = self.aem_customer_super_user
        ClientFactory(company=user.company)

        client_to_add_customer_to = user.company.client.first()
        self.valid_add_customer_request['client'] = client_to_add_customer_to.id

        self._test_list_create_customer_view_permissions(user=user,
                                                         data=self.valid_add_customer_request,
                                                         expected_status_code=status.HTTP_201_CREATED,
                                                         response_keys=('id', 'name', 'account_number', 'mobile_number',
                                                                        'landline_number', 'email', 'description',
                                                                        'system_details'))

        self.assertEqual(len(client_to_add_customer_to.customer.all()), 1)

        new_customer = client_to_add_customer_to.customer.get(name=self.valid_add_customer_request['name'])
        self.assertIsNotNone(new_customer)
        self.assertEqual(new_customer.client.company.id, self.aem_customer_super_user.company.id)

    def test_aem_customer_admin_can_create_customer(self):
        user = self.aem_customer_admin
        ClientFactory(company=user.company)

        client_to_add_customer_to = user.company.client.first()
        self.valid_add_customer_request['client'] = client_to_add_customer_to.id

        self._test_list_create_customer_view_permissions(user=user,
                                                         data=self.valid_add_customer_request,
                                                         expected_status_code=status.HTTP_201_CREATED,
                                                         response_keys=('id', 'name', 'account_number', 'mobile_number',
                                                                        'landline_number', 'email', 'description',
                                                                        'system_details'))

        self.assertEqual(len(client_to_add_customer_to.customer.all()), 1)

        new_customer = client_to_add_customer_to.customer.get(name=self.valid_add_customer_request['name'])
        self.assertIsNotNone(new_customer)
        self.assertEqual(new_customer.client.company.id, self.aem_customer_super_user.company.id)

    def test_aem_customer_user_cant_create_customer(self):
        user = self.aem_customer_admin
        ClientFactory(company=user.company)

        client_to_add_customer_to = user.company.client.first()
        self.valid_add_customer_request['client'] = client_to_add_customer_to.id

        self._test_list_create_customer_view_permissions(user=self.aem_employee,
                                                         data=self.valid_add_customer_request,
                                                         expected_status_code=status.HTTP_403_FORBIDDEN,
                                                         response_keys=('detail',))

    def test_cant_create_customer_for_different_company(self):
        company_one_user = self.aem_customer_super_user
        ClientFactory(company=company_one_user.company)

        company_two_user = self.aem_customer_super_user_company_two
        ClientFactory(company=company_two_user.company)

        company_one_client = company_one_user.company.client.first()
        self.valid_add_customer_request['client'] = company_one_client.id

        self._test_list_create_customer_view_permissions(user=company_two_user,
                                                         data=self.valid_add_customer_request,
                                                         expected_status_code=status.HTTP_403_FORBIDDEN,
                                                         response_keys=('detail',))
