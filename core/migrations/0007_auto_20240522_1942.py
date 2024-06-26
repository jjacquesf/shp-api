# Generated by Django 3.2.25 on 2024-05-23 00:17

from django.contrib.auth.models import Permission

from core import models
from django.db import migrations


def remove_theme_non_required_perms(apps, schema_editor):
    """remove non required permissions"""
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    content_type = ContentType.objects.get(
        model='theme',
        app_label='core',
    )
    # This cascades to Group
    Permission.objects.filter(
        content_type=content_type,
        codename__in=('delete_theme'),
    ).delete()

    Permission.objects.filter(
        content_type=content_type,
        codename__in=('add_theme'),
    ).delete()


def default_theme(apps, schema_editor):
    m1 = models.Theme(primary="#EBA900", secondary="#5A3F27", terciary="#D2D2D2", quaternary="#F7F8F8")
    ms = [m1]
    for x in ms:
        x.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_theme'),
    ]

    operations = [
        migrations.RunPython(remove_theme_non_required_perms, migrations.RunPython.noop),
        migrations.RunPython(default_theme),
    ]
