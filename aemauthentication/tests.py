from django.contrib.auth.models import Group
from django.test import TestCase, Client
from rest_framework.reverse import reverse

from aemauthentication.models import User


class UserTestCase(TestCase):

    def setUp(self):
        self.c = Client()

    def tearDown(self):
        for user in User.objects.all():
            user.delete()

    # AEM Super User Tests
    def aem_superuser_can_login(self):
        pass

    def aem_superuser_can_login_and_create_aem_admin(self):
        pass

    def aem_superuser_can_login_and_create_aem_employee(self):
        pass

    # AEM Admin Tests
    def aem_admin_can_login(self):
        pass

    def aem_admin_can_login_and_create_aem_employee(self):
        pass

    def aem_admin_can_login_and_cant_create_aem_admin(self):
        pass

    # AEM Employee Tests
    def aem_employee_can_login(self):
        pass

    def aem_employee_can_login_and_cant_create_aem_admin(self):
        pass

    def aem_employee_can_login_and_cant_create_aem_employee(self):
        pass

    # Customer Super Admin Tests
    def customer_super_admin_can_login(self):
        pass

    def customer_super_admin_can_login_and_create_customer_admin(self):
        pass

    def customer_super_admin_can_login_and_create_customer_user(self):
        pass

    # Customer Admin Tests
    def customer_admin_can_login(self):
        pass

    def customer_admin_can_login_and_create_customer_user(self):
        pass

    def customer_admin_can_login_and_cant_create_customer_admin(self):
        pass

    # Customer User Tests
    def customer_user_can_login(self):
        pass

    def customer_user_can_login_and_cant_create_customer_admin(self):
        pass

    def customer_user_can_login_and_cant_create_customer_user(self):
        pass
