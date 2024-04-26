# code
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core import models

@receiver(pre_save, sender=models.EvidenceAuth) 
def update(sender, instance, **kwargs):
    instance.version = instance.version + 1