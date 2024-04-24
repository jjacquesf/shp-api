# code
from django.db.models.signals import post_save
from django.dispatch import receiver

from core import models

@receiver(post_save, sender=models.EvidenceQualityControl) 
def create(sender, instance, created, **kwargs):
    if created:
        models.Notification.objects.create(
            evidence=instance.evidence,
            user=instance.evidence.owner,
            content=f'Hallazgo creado {instance.quality_control.name} en {instance.evidence.type.name}'
        )

@receiver(post_save, sender=models.EvidenceQualityControl) 
def save(sender, instance, **kwargs):
    models.Notification.objects.create(
        evidence=instance.evidence,
        user=instance.evidence.owner,
        content=f'Hallazgo actualizado {instance.quality_control.name} en {instance.evidence.type.name}'
    )