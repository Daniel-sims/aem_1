import uuid

import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models

from company.models import Company


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, username, email, password, company=None):
        """
        Creates a default user
        """
        user = self.model(username=username, email=self.normalize_email(email), company=company)
        user.set_password(password)
        user.save()

        return user

    def create_aem_customer_admin(self, username, email, password, company):
        """
        Creates an AEM Customer Admin for Admins at a customers company to use
        """
        if company is None:
            raise TypeError('AEM Customer Admins must be linked to a company.')

        user = self.create_user(username, email, password, company)
        user.is_aem_customer_admin = True
        user.save()

        return user

    def create_aem_admin(self, username, email, password):
        """
        Creates an AEM Admin for AEM Employees
        """
        user = self.create_user(username, email, password)
        user.is_aem_admin = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
        There are 3 kinds of users. An AEM Admin, a AEM Customer Admin and a default User role.

        An AEM Admin has privileges to setup companies and users
            - Create/Read/Update(full)/Delete Company
            - Create/Read/Update(full)/Delete User (linked to company - AEM Customer Admin & Default User)

        An AEM Customer Admin has fill privileges within their respective company with privileges;
            - Create/Read/Update(full)/Delete User (linked to company - Default User)
            - Create/Read/Update(full)/Delete Client (linked to company)
            - Create/Read/Update(full)/Delete Customer (linked to company/Client)
            - Create/Read/Update(full)/Delete Job (linked to company)

        A default User is an employee of the customers company, generally these will be seperated out
        into office staff (Creating Jobs and assigning to Engineers) and Engineers (Reading jobs). These
        are set via the permissions on the User that Django creates;
            Office Staff
            - Create/Read/Update/Delete Job
            - Create/Read/Update/Delete Client
            - Create/Read/Update/Delete Customer

            Engineer
            - Read Job
            - Read Client
            - Read Customer

        The idea behind this hierarchy is to allow for AEM Admins to setup clients so that they can initially log in
        to the app. The flow for this would be;

        Customer A signs up for AEM.

        AEM Admin creates Customer A a new AEM Customer Admin account (is_company_admin=True)

        Customer A creates new Default User accounts Engineer A, B and C

        Customer A(Admin) creates Customer list for Company.

        Customer A(Admin) creates a new Job for Engineer A

        Engineer A opens app to view the job
    """

    # Used to Log into the app with
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # Can de-activate individual Users to stop access to the App.
    is_active = models.BooleanField(default=True)

    # Date the User was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Date the User info was last updated
    updated_at = models.DateTimeField(auto_now=True)

    # Date the User last logged into the app
    last_active = models.DateTimeField(auto_now=True)

    email = models.EmailField(db_index=True, unique=True)

    # An Admin is a member of AEM staff who has full control over all users.
    is_aem_admin = models.BooleanField(default=False)

    # A Staff member is a AEM Customers Admin level with full control over all users in their company
    # who aren't staff. An AEM Customers Admin will also have the is_superuser field set to True.
    is_aem_customer_admin = models.BooleanField(default=False)

    # The company which this user is associated with.
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

