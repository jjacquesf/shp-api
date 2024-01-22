"""
Database models
"""
from django.utils.translation import gettext_lazy as _
import eav
from eav.models import Attribute
from typing import Any

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
    description = models.TextField(
        blank=True, 
        null=True
    )

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

class Entity(models.Model):
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
        verbose_name = _('Entity')
        verbose_name_plural = _('Entities')

class StateOrg(models.Model):
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
        verbose_name = _('State Organization')
        verbose_name_plural = _('State organizations')


class SifUser(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    stateorg = models.ForeignKey(
        StateOrg,
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = _('SIF user')
        verbose_name_plural = _('SIF users')

class SianUser(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    stateorg = models.ForeignKey(
        StateOrg,
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = _('SIAN user')
        verbose_name_plural = _('SIAN users')
class EvidenceGroup(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    alias = models.SlugField(max_length=128,unique=True)
    description = models.TextField(
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = _('Evidence group')
        verbose_name_plural = _('Evidence groups')

class EvidenceStage(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    position = models.IntegerField(default=1)
    description = models.TextField(
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = _('Evidence stage')
        verbose_name_plural = _('Evidence stages')

class EvidenceStatus(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    position = models.IntegerField(default=1)
    color = models.TextField()
    description = models.TextField(
        blank=True, 
        null=True
    )
    stage = models.ForeignKey(
        EvidenceStage,
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        EvidenceGroup,
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = _('Evidence satatus')
        verbose_name_plural = _('Evidence satatuses')

class CustomField(models.Model):
    is_active = models.BooleanField(default=True)
    catalog = models.TextField(
        blank=True, 
        null=True
    )
    description = models.TextField(
        blank=True, 
        null=True
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('Custom field')
        verbose_name_plural = _('Custom field')
    
    def __str__(self):
        return self.attribute.name

    @staticmethod
    def create_custom_field(**kwargs: Any):

        is_active = kwargs.pop('is_active', True)
        catalog = kwargs.pop('catalog', None)
        description = kwargs.pop('description', None)

        attribute = Attribute.objects.create(**kwargs)

        model = CustomField.objects.create(
            is_active=is_active,
            catalog=catalog,
            description=description,
            attribute=attribute
        )

        return model


class EvidenceType(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    alias = models.SlugField(max_length=128,unique=True)
    level = models.IntegerField(default=0)
    attachment_required = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, 
        null=True
    )
    group = models.ForeignKey(
        EvidenceGroup,
        on_delete=models.CASCADE
    )
    custom_fields = models.ManyToManyField(CustomField, through='EvidenceTypeCustomField')
    description = models.TextField(
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = _('Evidence type')
        verbose_name_plural = _('Evidence types')

class EvidenceTypeCustomField(models.Model):
    evidence_type = models.ForeignKey(
        EvidenceType,
        on_delete=models.CASCADE
    )
    custom_field = models.ForeignKey(
        CustomField,
        on_delete=models.CASCADE
    )
    mandatory = models.BooleanField(default=False)

    class Meta:
        unique_together = [['evidence_type', 'custom_field']]

## Register eav for models
eav.register(EvidenceGroup)
eav.register(Dpe)