from django.apps import AppConfig


class EvidenceCommentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evidence_comment'


    def ready(self):
        import evidence_comment.signals