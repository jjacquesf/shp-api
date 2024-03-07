# Generated by Django 3.2.23 on 2024-02-24 14:21

from django.db import migrations
from core import models

def default_evidence_groups(apps, schema_editor):
    m1 = models.EvidenceGroup(name="Auditoría interna", alias="internal", description="Auditoría interna")
    m2 = models.EvidenceGroup(name="Documentos confidenciales", alias="confidencial", description="Documentos confidenciales")
    m3 = models.EvidenceGroup(name="Entregables de terceros", alias="third-party", description="Entregables de terceros")
    ms = [m1, m2, m3]
    for x in ms:
        x.save()

def default_evidence_stage(apps, schema_editor):
    m1 = models.EvidenceStage(name="Pendiente", position=1, description="Pendiente")
    m2 = models.EvidenceStage(name="En proceso", position=2, description="En proceso")
    m3 = models.EvidenceStage(name="Terminado", position=3, description="Terminado")
    ms = [m1, m2, m3]
    for x in ms:
        x.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_rename_evidencetypequalitycontrol_qualitycontrol'),
    ]

    operations = [
        migrations.RunPython(default_evidence_groups),
        migrations.RunPython(default_evidence_stage),
    ]
