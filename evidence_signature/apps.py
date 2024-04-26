from django.apps import AppConfig


class EvidenceSignatureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evidence_signature'

    def ready(self):
        import evidence_signature.signals