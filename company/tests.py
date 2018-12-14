from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from aemauthentication.factories import AemGroupFactory, UserFactory


class CreateClientTestCase(APITestCase):

    def setUp(self):
        self.aem_admin_group = AemGroupFactory.create(
            slug_field=settings.AEM_ADMIN_SLUG_FIELD,
            linked_group__name="Aem Admin",
            can_add_permission_slugs=(
                settings.AEM_EMPLOYEE_SLUG_FIELD,
            ),
            company_permissions=(
                'Can add company',
            )
        )

        self.aem_employee_group = AemGroupFactory.create(
            slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD,
            linked_group__name="Aem Employee",
            can_add_permission_slugs=(

            ),
            company_permissions=(
                'Can add company',
            )
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
        response = self.client.post(reverse('list-create-company'), data, format='json')

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if response_contains_kvp:
            for kvp in response_contains_kvp:
                response_field = response.json()[kvp[0]]
                self.assertIsNotNone(response_field)
                if kvp[1]:
                    self.assertTrue(kvp[1], response_field)

    def test_aem_admin_can_create_company(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))

        self._test_permission(user=user, data={
            "name": "Company",
            "super_user_username": "CompanySu",
            "super_user_password": "12345678",
            "super_user_email": "CompanySu@email.com"
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('name', 'Company'),
                              ))

    def test_aem_employee_can_create_company(self):
        user = UserFactory.create(groups=(self.aem_employee_group,))

        self._test_permission(user=user, data={
            "name": "Company",
            "super_user_username": "CompanySu",
            "super_user_password": "12345678",
            "super_user_email": "CompanySu@email.com"
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('name', 'Company'),
                              ))

    def test_aem_customer_super_user_cant_create_company(self):
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,))

        self._test_permission(user=user, data={
            "name": "Company",
            "super_user_username": "CompanySu",
            "super_user_password": "12345678",
            "super_user_email": "CompanySu@email.com"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create a company.'),
                              ))

    def test_aem_customer_admin_cant_create_company(self):
        user = UserFactory.create(groups=(self.aem_customer_admin_group,))

        self._test_permission(user=user, data={
            "name": "Company",
            "super_user_username": "CompanySu",
            "super_user_password": "12345678",
            "super_user_email": "CompanySu@email.com"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create a company.'),
                              ))

    def test_aem_customer_user_cant_create_company(self):
        user = UserFactory.create(groups=(self.aem_customer_user_group,))

        self._test_permission(user=user, data={
            "name": "Company",
            "super_user_username": "CompanySu",
            "super_user_password": "12345678",
            "super_user_email": "CompanySu@email.com"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              response_contains_kvp=(
                                  ('detail', 'Invalid permissions to create a company.'),
                              ))

    def test_cant_create_company_with_same_super_user_name(self):
        user = UserFactory.create(groups=(self.aem_admin_group,))

        self._test_permission(user=user, data={
            "name": "Company",
            "super_user_username": "CompanySu",
            "super_user_password": "12345678",
            "super_user_email": "CompanySu@email.com"
        }, expected_status_code=status.HTTP_201_CREATED,
                              response_contains_kvp=(
                                  ('name', 'Company'),
                              ))

        self._test_permission(user=user, data={
            "name": "Company",
            "super_user_username": "CompanySu",
            "super_user_password": "12345678",
            "super_user_email": "CompanySu@email.com"
        }, expected_status_code=status.HTTP_400_BAD_REQUEST,
                              response_contains_kvp=(
                                  ('errors', 'User already exists.'),
                              ))



