# Generated by Django 3.2.23 on 2024-01-29 02:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20240128_2301'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EvidenceTypeQualityControl',
            new_name='QualityControl',
        ),
    ]
