from django.apps import AppConfig


class EvidenceAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evidence_auth'

    def ready(self):
        import evidence_auth.signals