# code
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from core import models
from django.core.mail import send_mail


@receiver(post_save, sender=models.ResetPassword) 
def create(sender, instance, created, **kwargs):
    if created:
        subject = 'Solicitud de cambio de contraseña'
        url = f"http://localhost:5173/reset-password/{instance.token}"
        message = f"""
            Hola {instance.user.name}

            Hemos recibido uan solicitud para recuperar tu contraseña, 
            para continuar con el proceso haz click en el siguiente enlace:

            {url}
        """
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.user.email]
        send_mail(subject, message, email_from, recipient_list)