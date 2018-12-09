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
                settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
                settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
        )

        self.aem_employee_group = AemGroupFactory.create(
            slug_field=settings.AEM_EMPLOYEE_SLUG_FIELD,
            linked_group__name="Aem Employee",
            can_add_permission_slugs=(
                settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
                settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            )
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
        response = self.client.post(reverse('create-user'), data)

        self.assertEqual(response.status_code, expected_status_code, response.content)

        if expected_detail_message:
            self.assertEqual(response.content, expected_detail_message)

    """
    AEM Admin
    
    The AEM Admin tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Able to create an account of type; aem-employee
    - Not able to create an account of type aem-employee when request contains a company
    
    - Not able to create an account of type; aem-customer-super-user 
    
    - Able to create an account of type aem-customer-admin with a company that exists
    - Not able to create an account of type aem-customer-admin with a company that doesn't exist
    
    - Able to create an account of type aem-customer-user with a company that exists
    - Not able to create an account of type aem-customer-user with a company that doesn't exist
    """

    def test_aem_admin_cant_create_aem_admin(self):
        """
        An AEM Admin can't create an account for an AEM Admin.
        """
        user = UserFactory.create(groups=(self.aem_admin_group,))

        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_admin_can_create_aem_employee(self):
        """
        An AEM Admin can create an account for an AEM Employee.
        """
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":null,"email":"newAemEmployee@outlook.com","username":"newAemEmployee"}')

    def test_aem_admin_cant_create_aem_employee_with_company(self):
        """
        An AEM Admin can't create an account for an AEM Employee with a company in the request.

        AEM Staff accounts cannot be assigned to a company.
        """
        valid_company = CompanyFactory.create(company_id='valid-company-id')
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD,
            "company": valid_company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"A AEM Admin or AEM Employee account cannot be associated with a company."}')

    def test_aem_admin_cant_create_aem_customer_super_user_company_exists(self):
        """
        An AEM Admin can't create an account for an AEM Customer Super User.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        valid_company = CompanyFactory.create(company_id='valid-company-id')
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
            "company": valid_company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_admin_can_create_aem_customer_admin_correct_company_exists(self):
        """
        An AEM Admin can create an account for an AEM Customer Admin.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_admin_group,),
                                  company=CompanyFactory.create(company_id='valid-company-id'))
        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":"valid-company-id","email":"newAemCustomerAdmin@outlook.com","username":"newAemCustomerAdmin"}')

    def test_aem_admin_cant_create_aem_customer_admin_company_doesnt_exist(self):
        """
        An AEM Admin can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_admin_group,))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": "invalid-company-id"
        }, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_aem_admin_can_create_aem_customer_user_correct_company_exists(self):
        """
        An AEM Admin can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        valid_company = CompanyFactory.create(company_id='valid-company-id')
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": valid_company.company_id
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":"valid-company-id","email":"newAemCustomerUser@outlook.com","username":"newAemCustomerUser"}')

    def test_aem_admin_cant_create_aem_customer_user_company_doesnt_exist(self):
        """
        An AEM Admin can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_admin_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": "invalid-company-id"
        }, expected_status_code=status.HTTP_400_BAD_REQUEST)

    """
    AEM Employee

    The AEM Employee tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-employee
    - Not able to create an account of type; aem-customer-super-user 
    
    - Able to create an account of type aem-customer-admin with a company that exists
    - Not able to create an account of type aem-customer-admin with a company that doesn't exist
    
    - Able to create an account of type aem-customer-user with a company that exists
    - Not able to create an account of type aem-customer-user with a company that doesn't exist
    """

    def test_aem_employee_cant_create_aem_admin(self):
        """
        An AEM Employee can't create an account for an AEM Admin.
        """
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_employee_cant_create_aem_employee(self):
        """
        An AEM Employee can't create an account for an AEM Employee.
        """
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_employee_cant_create_aem_customer_super_user_company_exists(self):
        """
        An AEM Employee can't create an account for an AEM Customer Super User.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        valid_company = CompanyFactory.create(company_id='valid-company-id')
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
            "company": valid_company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_employee_can_create_aem_customer_admin_correct_company_exists(self):
        """
        An AEM Employee can create an account for an AEM Customer Admin.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        valid_company = CompanyFactory.create(company_id='valid-company-id')
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": valid_company.company_id
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":"valid-company-id","email":"newAemCustomerAdmin@outlook.com","username":"newAemCustomerAdmin"}')

    def test_aem_employee_cant_create_aem_customer_admin_company_doesnt_exist(self):
        """
        An AEM Employee can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": "invalid-company-id"
        }, expected_status_code=status.HTTP_400_BAD_REQUEST)

    def test_aem_employee_can_create_aem_customer_user_correct_company_exists(self):
        """
        An AEM Employee can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        valid_company = CompanyFactory.create(company_id='valid-company-id')
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": valid_company.company_id
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":"valid-company-id","email":"newAemCustomerUser@outlook.com","username":"newAemCustomerUser"}')

    def test_aem_employee_cant_create_aem_customer_user_company_doesnt_exist(self):
        """
        An AEM Employee can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_employee_group,))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": "invalid-company-id"
        }, expected_status_code=status.HTTP_400_BAD_REQUEST)

    """
    AEM Customer Super User

    The AEM Customer Super User tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-employee
    - Not able to create an account of type; aem-customer-super-user
    
    - Able to create an account of type aem-customer-admin with a company that exists
    - Not able to create an account of type aem-customer-admin with a company that doesn't exist
    - Not able to create an account of type aem-customer-admin with a company id that is different to the AEM Customer Super Users
    
    - Able to create an account of type aem-customer-user with a company that exists
    - Not able to create an account of type aem-customer-user with a company that doesn't exist
    - Not able to create an account of type aem-customer-user with a company id that is different to the AEM Customer Super Users
    """

    def test_aem_customer_super_user_cant_create_aem_admin(self):
        """
        An AEM Customer Super User can't create an account for an AEM Admin.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_super_user_cant_create_aem_employee(self):
        """
        An AEM Customer Super User can't create an account for an AEM Employee.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_super_user_cant_create_aem_customer_super_user(self):
        """
        An AEM Customer Super User can't create an account for an AEM Customer Super User.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_super_user_can_create_aem_customer_admin_correct_company_exists(self):
        """
        An AEM Customer Super User can create an account for an AEM Customer Admin.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemCustomerAdmin",
            "email": "newAemCustomerAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":"users-company-id","email":"newAemCustomerAdmin@outlook.com","username":"newAemCustomerAdmin"}')

    def test_aem_customer_super_user_cant_create_aem_customer_admin_company_doesnt_exist(self):
        """
        An AEM Customer Super User can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='valid-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": "invalid-company-id"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"You cannot create a user that is not in your company."}')

    def test_aem_customer_super_user_cant_create_aem_customer_admin_different_company_id(self):
        """
        An AEM Customer Super User can create an account for an AEM Customer Admin account.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": CompanyFactory.create(company_id='different-company-id').company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    def test_aem_customer_super_user_can_create_aem_customer_user_correct_company_exists(self):
        """
        An AEM Customer Super User can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":"users-company-id","email":"newAemCustomerUser@outlook.com","username":"newAemCustomerUser"}')

    def test_aem_customer_super_user_cant_create_aem_customer_user_company_doesnt_exist(self):
        """
        An AEM Customer Super User can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))
        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": "invalid-company-id"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"You cannot create a user that is not in your company."}')

    def test_aem_customer_super_user_cant_create_aem_customer_user_different_company_id(self):
        """
        An AEM Customer Super User can create an account for an AEM Customer User account.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_super_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": CompanyFactory.create(company_id='different-company-id').company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    """
    AEM Customer Admin

    The AEM Customer Admin tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-employee
    - Not able to create an account of type; aem-customer-super-user
    - Not able to create an account of type; aem-customer-admin

    - Able to create an account of type aem-customer-user with a company that exists
    - Not able to create an account of type aem-customer-user with a company that doesn't exist
    - Not able to create an account of type aem-customer-user with a company id that is different to the AEM Customer Super Users
    """

    def test_aem_customer_admin_cant_create_aem_admin(self):
        """
        An AEM Customer Admin can't create an account for an AEM Admin.
        """
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_admin_cant_create_aem_employee(self):
        """
        An AEM Customer Admin can't create an account for an AEM Employee.
        """
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_admin_cant_create_aem_customer_super_user(self):
        """
        An AEM Customer Admin can't create an account for an AEM Customer Super User.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_admin_cant_create_aem_customer_admin(self):
        """
        An AEM Customer Admin can't create an account for an AEM Customer Admin.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_admin_can_create_aem_customer_user_correct_company_exists(self):
        """
        An AEM Customer Admin can create an account for an AEM Customer User.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_201_CREATED,
                              expected_detail_message=b'{"company":"users-company-id","email":"newAemCustomerUser@outlook.com","username":"newAemCustomerUser"}')

    def test_aem_customer_admin_cant_create_aem_customer_user_company_doesnt_exist(self):
        """
        An AEM Customer Admin cant create an account for a AEM Customer User for a company that doesn't exist.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": "invalid-company-id"
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"You cannot create a user that is not in your company."}')

    def test_aem_customer_admin_cant_create_aem_customer_user_different_company_id(self):
        """
        An AEM Customer Super User can create an account for an AEM Customer User account.

        When creating a Customer Admin or Customer User it must be assigned to a company. If the user making
        the request is not of type AEM Super User, AEM Admin or AEM Employee the users company must match
        the new users company id.
        """
        user = UserFactory.create(groups=(self.aem_customer_admin_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemCustomerUser",
            "email": "newAemCustomerUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": CompanyFactory.create(company_id='different-company-id').company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN)

    """
    AEM Customer User

    The AEM Customer User tests cover the scenarios;
    - Not able to create an account of type; aem-admin
    - Not able to create an account of type; aem-employee
    - Not able to create an account of type; aem-customer-super-user
    - Not able to create an account of type; aem-customer-admin
    - Not able to create an account of type; aem-customer-user
    """

    def test_aem_customer_user_cant_create_aem_admin(self):
        """
        An AEM Customer User can't create an account for an AEM Admin.
        """
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemAdmin",
            "email": "newAemAdmin@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_ADMIN_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_user_cant_create_aem_employee(self):
        """
        An AEM Customer User can't create an account for an AEM Employee.
        """
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newAemEmployee",
            "email": "newAemEmployee@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_EMPLOYEE_SLUG_FIELD
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_user_cant_create_aem_customer_super_user(self):
        """
        An AEM Customer User can't create an account for an AEM Customer Super User.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_SUPER_USER_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_user_cant_create_aem_customer_admin(self):
        """
        An AEM Customer User can't create an account for an AEM Customer Admin.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_ADMIN_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

    def test_aem_customer_user_cant_create_aem_customer_admin(self):
        """
        An AEM Customer User can't create an account for an AEM Customer Admin.

        AEM Customer Super Users can only be created when a company is created or by an AEM Super User.
        """
        user = UserFactory.create(groups=(self.aem_customer_user_group,),
                                  company=CompanyFactory.create(company_id='users-company-id'))

        self._test_permission(user=user, data={
            "username": "newCustomerSuperUser",
            "email": "newCustomerSuperUser@outlook.com",
            "password": "Passw0rd01",
            "aem_group": settings.AEM_CUSTOMER_USER_SLUG_FIELD,
            "company": user.company.company_id
        }, expected_status_code=status.HTTP_403_FORBIDDEN,
                              expected_detail_message=b'{"detail":"Invalid permissions to create this account type."}')

