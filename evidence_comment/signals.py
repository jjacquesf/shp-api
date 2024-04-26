# code
from django.db.models.signals import post_save
from django.dispatch import receiver

from core import models

@receiver(post_save, sender=models.EvidenceComment) 
def create(sender, instance, created, **kwargs):
    if created:
        models.Notification.objects.create(
            evidence=instance.evidence,
            user=instance.evidence.owner,
            co=f'Nuevo comentario en {instance.evidence.type.name}'
        )
