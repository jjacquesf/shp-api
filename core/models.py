"""
Database models
"""
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group
)
from django.contrib.auth import get_user_model

class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError(_('User must have an email address'))
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create, save ans return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    job_position = models.CharField(max_length=255)

class CustomGroup(Group):
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

class Municipality(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    class Meta:
        verbose_name = _('Municipality')
        verbose_name_plural = _('Municipalities')

class Institution(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    class Meta:
        verbose_name = _('Institution')


class Dpe(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    class Meta:
        verbose_name = _('Decentralized public entity')
        verbose_name_plural = _('Decentralized public entities')

class Supplier(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    tax_id = models.CharField(max_length=13,unique=True)
    tax_name = models.CharField(max_length=255,unique=True)
    class Meta:
        verbose_name = _('Supplier')

class Department(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    level = models.IntegerField(default=0)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, 
        null=True
    )
    class Meta:
        verbose_name = _('SHP Department')
        verbose_name_plural = _('SHP Departments')

