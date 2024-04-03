"""
Database models
"""
import os

from django.core.files.storage import FileSystemStorage
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from django.utils.translation import gettext_lazy as _
from app import settings
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

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

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

class CustomGroup(Group):
    description = models.TextField(
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
class Profile(TimeStampMixin):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    job_position = models.CharField(max_length=255)

class Municipality(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    class Meta:
        verbose_name = _('Municipality')
        verbose_name_plural = _('Municipalities')

class Institution(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    class Meta:
        verbose_name = _('Institution')

class Dpe(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    class Meta:
        verbose_name = _('Decentralized public entity')
        verbose_name_plural = _('Decentralized public entities')

class Supplier(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    tax_id = models.CharField(max_length=13,unique=True)
    tax_name = models.CharField(max_length=255,unique=True)
    class Meta:
        verbose_name = _('Supplier')

class Department(TimeStampMixin):
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

class Entity(TimeStampMixin):
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

class StateOrg(TimeStampMixin):
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

class SifUser(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    stateorg = models.ForeignKey(
        StateOrg,
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = _('SIF user')
        verbose_name_plural = _('SIF users')

class SianUser(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128,unique=True)
    stateorg = models.ForeignKey(
        StateOrg,
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = _('SIAN user')
        verbose_name_plural = _('SIAN users')
class EvidenceGroup(TimeStampMixin):
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

class EvidenceStage(TimeStampMixin):
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

class EvidenceStatus(TimeStampMixin):
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

        unique_together = ('stage', 'group', 'name')

class CustomField(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    # Catalog name to prefill
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
            attribute=attribute,
        )

        return model
    
class QualityControl(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128, unique=True)

class EvidenceType(TimeStampMixin):
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
    quality_controls = models.ManyToManyField(QualityControl, through='EvidenceTypeQualityControl')
    description = models.TextField(
        blank=True, 
        null=True
    )
    signature_required = models.BooleanField(default=False)
    auth_required = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('Evidence type')
        verbose_name_plural = _('Evidence types')



class EvidenceTypeCustomField(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    type = models.ForeignKey(
        EvidenceType,
        on_delete=models.CASCADE
    )
    custom_field = models.ForeignKey(
        CustomField,
        on_delete=models.CASCADE
    )
    mandatory = models.BooleanField(default=False)
    group = models.CharField(max_length=64, default="General")
    class Meta:
        unique_together = [['type', 'custom_field']]

    def __str__(self):
        return f'{self.type.is_active} / {self.type.id} / {self.custom_field.id}'
    
class EvidenceTypeQualityControl(TimeStampMixin):
    is_active = models.BooleanField(default=True)
    type = models.ForeignKey(
        EvidenceType,
        on_delete=models.CASCADE
    )
    quality_control = models.ForeignKey(
        QualityControl,
        on_delete=models.CASCADE
    )
    class Meta:
        unique_together = [['type', 'quality_control']]

    def __str__(self):
        return f'{self.type.is_active} / {self.type.id} / {self.quality_control.id}'


def get_upload_path(instance, filename):
    return os.path.join(
      "user_%d" % instance.owner.id, filename)

class UploadedFile(models.Model):
    file = models.FileField(storage=FileSystemStorage(location=settings.MEDIA_ROOT), upload_to=get_upload_path)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    uploaded_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.uploaded_on.date()

class Evidence(TimeStampMixin):
    history = AuditlogHistoryField()

    status = models.ForeignKey(
        EvidenceStatus,
        on_delete=models.CASCADE
    )
    dirty = models.BooleanField(default=False)
    type = models.ForeignKey(
        EvidenceType,
        on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, 
        null=True
    )
    pending_auth = models.BooleanField(default=False)
    pending_signature = models.BooleanField(default=False)
    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        blank=True, 
        null=True
    )
    version = models.IntegerField(default=0)

class EvidenceFinding(TimeStampMixin):
    class Status(models.TextChoices):
        PENDING = 'PEN', _('Pending')
        SENT = 'SEN', _('Sent')
        WAITING_FOR_REVIEW = 'WAI', _('Waiting for review')
        REVIEWED = 'REV', _('Reviewed')
        COMPLETED = 'COM', _('Completed')
        REJECTED = 'REJ', _('Rejected')

    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE
    )
    qc = models.ForeignKey(
        QualityControl,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.PENDING,
    )
    comments = models.TextField(
        blank=True, 
        null=True
    )
    version = models.IntegerField(default=1)
    

    class Meta:
        unique_together = ('evidence', 'qc', 'version')

class EvidenceAuth(TimeStampMixin):
    class Status(models.TextChoices):
        PENDING = 'PEN', _('Pending')
        COMPLETED = 'COM', _('Completed')
    
    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.PENDING,
    )
    version = models.IntegerField(default=1)
    

    class Meta:
        unique_together = ('evidence', 'user', 'version')


class EvidenceSignature(TimeStampMixin):
    class Status(models.TextChoices):
        PENDING = 'PEN', _('Pending')
        COMPLETED = 'COM', _('Completed')
    
    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.PENDING,
    )
    version = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ('evidence', 'user', 'version')


class EvidenceComment(TimeStampMixin):
    
    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    comments = models.CharField(max_length=512)
    
    class Meta:
        unique_together = ('evidence', 'user', 'comments')

## Register eav for models
eav.register(Evidence)

## Enable auditlog
auditlog.register(
    Evidence
)
