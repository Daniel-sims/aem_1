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

    def _test_permission(self, user, data, expected_status_code, response_contains_kvp=None):
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('create-user'), data, format='json')

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if response_contains_kvp:
            for kvp in response_contains_kvp:
                response_field = response.json()[kvp[0]]
                self.assertIsNotNone(response_field)
                self.assertTrue(kvp[1], response_field)

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
        user = UserFactory.create(groups=(self.aem_admin_group,))

        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_admin_can_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('username', 'newAemEmployee'),
                                  ('email', 'newAemEmployee@outlook.com'),
                              ))

        new_user = User.objects.get(username='newAemEmployee')
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.groups.filter(aemgroup__slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD).exists())
        self.assertIsNone(new_user.company)

    def test_aem_admin_cant_create_aem_customer_super_user(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_admin_cant_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_admin_can_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

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
        user = UserFactory.create(groups=(self.aem_employee_group,))

        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_employee_cant_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_employee_cant_create_aem_customer_super_user(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_employee_cant_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_employee_can_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

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
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_super_user_cant_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_super_user_cant_create_aem_customer_super_user(self):
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_super_user_can_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('company', user.company.company_id),
                                  ('username', 'newAemCustomerAdmin'),
                                  ('email', 'newAemCustomerAdmin@outlook.com'),
                              ))

        new_user = User.objects.get(username='newAemCustomerAdmin')
        self.assertIsNotNone(new_user)
        self.assertEqual(user.company, new_user.company)
        self.assertTrue(new_user.groups.filter(aemgroup__slug_field=settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD).exists())

    def test_aem_customer_super_user_can_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('company', user.company.company_id),
                                  ('username', 'newAemCustomerUser'),
                                  ('email', 'newAemCustomerUser@outlook.com'),
                              ))
        new_user = User.objects.get(username='newAemCustomerUser')
        self.assertIsNotNone(new_user)
        self.assertEqual(user.company, new_user.company)
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
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_admin_cant_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_admin_cant_create_aem_customer_super_user(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_admin_cant_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_admin_can_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('company', user.company.company_id),
                                  ('email', 'newAemCustomerUser@outlook.com'),
                                  ('username', 'newAemCustomerUser'),
                              ))

        new_user = User.objects.get(username='newAemCustomerUser')
        self.assertIsNotNone(new_user)
        self.assertEqual(user.company, new_user.company)
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
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_user_cant_create_aem_employee(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_user_cant_create_aem_customer_super_user(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_user_cant_create_aem_customer_admin(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))

    def test_aem_customer_user_cant_create_aem_customer_user(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id=uuid.uuid4()))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create this account type.'),
                              ))
