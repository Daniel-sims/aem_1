from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase

from aemauthentication.factories import GroupsFactory, AemGroupFactory, UserFactory
from aemauthentication.models import User
from aemauthentication.views import CreateUserAPIView
from groups.models import AemGroup


def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)


class UserTestCase(APITestCase):
    AEM_ADMIN_SLUG_FIELD = 'aem-admin'
    AEM_EMPLOYEE_SLUG_FIELD = 'aem-employee'
    AEM_CUSTOMER_ADMIN_SLUG_FIELD = 'aem-customer-admin'
    AEM_CUSTOMER_USER_SLUG_FIELD = 'aem-customer-user'

    def setUp(self):
        self.aem_admin_group = AemGroupFactory.create(
            slug_field=self.AEM_ADMIN_SLUG_FIELD,
            linked_group__name="Aem Admin",
            can_add_permission_slugs=(
                self.AEM_EMPLOYEE_SLUG_FIELD,
                self.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
                self.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
        )

        self.aem_employee_group = AemGroupFactory.create(
            slug_field=self.AEM_EMPLOYEE_SLUG_FIELD,
            linked_group__name="Aem Employee",
            can_add_permission_slugs=(
                self.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
                self.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
        )

        self.aem_customer_admin_group = AemGroupFactory.create(
            slug_field=self.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            linked_group__name="Aem Customer Admin",
            can_add_permission_slugs=(
                self.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
        )

        self.aem_customer_user_group = AemGroupFactory.create(
            slug_field=self.AEM_CUSTOMER_USER_SLUG_FIELD,
            linked_group__name="Aem Customer User",
            can_add_permission_slugs=())

    def tearDown(self):
        pass

    def _test_permission(self, user, data, expected_status_code):
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('create-user'), data)

        self.assertEqual(response.status_code, expected_status_code)

    def test_aem_admin_user_cant_create_aem_admin(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_admin_user_can_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmlpoyee",
            "email": "newAemEmlpoyee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED)

    def test_aem_admin_user_can_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerAdmin",
            "email": "newCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED)

    def test_aem_admin_user_can_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerUser",
            "email": "newCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_USER_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED)

    def test_aem_employee_cant_create_aem_admin(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_employee_cant_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmlpoyee",
            "email": "newAemEmlpoyee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_employee_can_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerAdmin",
            "email": "newCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED)

    def test_aem_employee_can_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerUser",
            "email": "newCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_USER_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED)

    def test_aem_customer_admin_user_cant_create_aem_admin(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_customer_admin_user_cant_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmlpoyee",
            "email": "newAemEmlpoyee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_customer_admin_user_cant_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerAdmin",
            "email": "newCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_customer_admin_user_can_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerUser",
            "email": "newCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_USER_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED)

    def test_aem_customer_user_cant_create_aem_admin(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,))
        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_customer_user_cant_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmlpoyee",
            "email": "newAemEmlpoyee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_customer_user_cant_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerAdmin",
            "email": "newCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_customer_user_cant_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerUser",
            "email": "newCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": self.AEM_CUSTOMER_USER_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN)
