import uuid

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from django.conf import settings
from aemauthentication.factories import GroupsFactory, AemGroupFactory, UserFactory
from aemauthentication.models import User
from aemauthentication.views import CreateUserAPIView
from company.factories import CompanyFactory
from groups.models import AemGroup


class CreateUserTestCase(APITestCase):
    valid_add_user_request = {
        "username": "NewUser",
        "email": "NewUser@outlook.com",
        "password": "Passw0rd01",
        "aem_group": ""
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

    def _test_create_user_view_permissions(self, user, data, expected_status_code, response_keys=None):
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('create-user'), data, format='json')

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if response_keys:
            for key in response_keys:
                response_field = response.json()[key]
                self.assertIsNotNone(response_field)

    """
    AEM Admin
    
    The AEM Admin tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Able to create an account of type; aem-admin
    - Not able to create an account of type; aem-customer-super-user
    - Not able to create an account of type; aem-customer-admin
    - Not able to create an account of type; aem-customer-user
    """

    def test_aem_admin_cant_create_aem_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_admin_can_create_aem_employee(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_EMPLOYEE_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_201_CREATED,
                                                response_keys=('username', 'email',))

        new_user = User.objects.get(username=self.valid_add_user_request['username'])
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.groups.filter(aemgroup__slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD).exists())

    def test_aem_admin_cant_create_aem_customer_super_user(self):
        self._test_create_user_view_permissions(user=self.aem_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_admin_cant_create_aem_customer_admin(self):
        self._test_create_user_view_permissions(user=self.aem_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_admin_can_create_aem_customer_user(self):
        self._test_create_user_view_permissions(user=self.aem_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    """
    AEM Employee

    The AEM Employee tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-customer-super-user
    - Not able to create an account of type; aem-customer-admin
    - Not able to create an account of type; aem-customer-user
    """

    def test_aem_employee_cant_create_aem_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_employee,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_employee_cant_create_aem_employee(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_EMPLOYEE_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_employee,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_employee_cant_create_aem_customer_super_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_employee,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_employee_cant_create_aem_customer_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_employee,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_employee_can_create_aem_customer_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_employee,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    """
    AEM Customer Super User

    The AEM Customer Super User tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-customer-super-user
    - Able to create an account of type; aem-customer-admin
    - Able to create an account of type; aem-customer-user
    """

    def test_aem_customer_super_user_cant_create_aem_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_super_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_super_user_cant_create_aem_employee(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_EMPLOYEE_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_super_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_super_user_cant_create_aem_customer_super_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_super_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_super_user_can_create_aem_customer_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_super_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_201_CREATED,
                                                response_keys=('username', 'email',))

        new_user = User.objects.get(username=self.valid_add_user_request['username'])
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.groups.filter(aemgroup__slug_field=settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD).exists())

    def test_aem_customer_super_user_can_create_aem_customer_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_super_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_201_CREATED,
                                                response_keys=('username', 'email',))

        new_user = User.objects.get(username=self.valid_add_user_request['username'])
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.groups.filter(aemgroup__slug_field=settings.AEM_CUSTOMER_USER_SLUG_FIELD).exists())

    """
    AEM Customer Admin

    The AEM Customer Admin tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-customer-super-user
    - Not able to create an account of type; aem-customer-admin
    - Able to create an account of type; aem-customer-user
    """

    def test_aem_customer_admin_cant_create_aem_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_admin_cant_create_aem_employee(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_EMPLOYEE_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_admin_cant_create_aem_customer_super_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_admin_cant_create_aem_customer_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_admin_can_create_aem_customer_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_admin,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_201_CREATED,
                                                response_keys=('username', 'email',))

        new_user = User.objects.get(username=self.valid_add_user_request['username'])
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.groups.filter(aemgroup__slug_field=settings.AEM_CUSTOMER_USER_SLUG_FIELD).exists())

    """
    AEM Customer User

    The AEM Customer User tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-customer-super-user
    - Not able to create an account of type; aem-customer-admin
    - Not able to create an account of type; aem-customer-user
    """

    def test_aem_customer_user_cant_create_aem_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_user_cant_create_aem_employee(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_EMPLOYEE_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_user_cant_create_aem_customer_super_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_user_cant_create_aem_customer_admin(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))

    def test_aem_customer_user_cant_create_aem_customer_user(self):
        self.valid_add_user_request['aem_group'] = settings.AEM_CUSTOMER_USER_SLUG_FIELD
        self._test_create_user_view_permissions(user=self.aem_customer_user,
                                                data=self.valid_add_user_request,
                                                expected_status_code=status.HTTP_403_FORBIDDEN,
                                                response_keys=('detail',))
