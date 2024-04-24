from django.apps import AppConfig


class EvidenceQualityControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evidence_quality_control'

    def ready(self):
        import evidence_quality_control.signals