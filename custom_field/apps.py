from django.apps import AppConfig


class CustomFieldConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_field'
