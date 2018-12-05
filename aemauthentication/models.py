import uuid

import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractUser, BaseUserManager,
    Group)
from django.db import models
from rest_framework.exceptions import ParseError

from company.models import Company


class UserQuerySet(models.QuerySet):
    def active_and_not_deleted(self):
        return self.filter(is_deleted=False, is_active=True)


class UserManager(BaseUserManager):

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).active_and_not_deleted()

    def create_user(self, username, email, password, aem_group=None, company=None):
        user = self.model(username=username, email=self.normalize_email(email), company=company)
        user.set_password(password)
        user.save()

        if aem_group:
            user.groups.add(aem_group)
            user.save()

        return user


class User(AbstractUser):
    # Date the User was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Date the User info was last updated
    updated_at = models.DateTimeField(auto_now=True)

    # Date the User last logged into the app
    last_active = models.DateTimeField(auto_now=True)

    # The company which this user is associated with.
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    # Indicates whether this user has been deleted or not
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
