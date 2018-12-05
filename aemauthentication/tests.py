from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.test import TestCase, Client
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
            slug_field=self.AEM_ADMIN_SLUG_FIELD,
            linked_group__name="Aem Customer Admin",
            can_add_permission_slugs=(
                self.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
        )

        self.aem_customer_user_group = AemGroupFactory.create(
            slug_field=self.AEM_EMPLOYEE_SLUG_FIELD,
            linked_group__name="Aem Customer User",
            can_add_permission_slugs=())

    def tearDown(self):
        pass

    def test_aem_admin_group_permissions(self):
        aem_admin = UserFactory.create(groups=(self.aem_admin_group,))
        self.assertEqual(len(get_user_permissions(aem_admin)), 3)
        self.assertSetEqual(
            aem_admin.get_all_permissions(),
            {
                'groups.can_add_{}'.format(self.AEM_EMPLOYEE_SLUG_FIELD),
                'groups.can_add_{}'.format(self.AEM_CUSTOMER_ADMIN_SLUG_FIELD),
                'groups.can_add_{}'.format(self.AEM_CUSTOMER_USER_SLUG_FIELD),
            }
        )

        aem_employee = UserFactory.create(groups=(self.aem_employee_group,))
        self.assertEqual(len(get_user_permissions(aem_employee)), 2)
        self.assertSetEqual(
            aem_employee.get_all_permissions(),
            {
                'groups.can_add_{}'.format(self.AEM_CUSTOMER_ADMIN_SLUG_FIELD),
                'groups.can_add_{}'.format(self.AEM_CUSTOMER_USER_SLUG_FIELD),
            }
        )

        aem_customer_admin = UserFactory.create(groups=(self.aem_customer_admin_group,))
        self.assertEqual(len(get_user_permissions(aem_customer_admin)), 1)
        self.assertSetEqual(
            aem_customer_admin.get_all_permissions(),
            {
                'groups.can_add_{}'.format(self.AEM_CUSTOMER_USER_SLUG_FIELD),
            }
        )

        aem_customer_user = UserFactory.create(groups=(self.aem_customer_user_group,))
        self.assertEqual(len(get_user_permissions(aem_customer_user)), 0)
