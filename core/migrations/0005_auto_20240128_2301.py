# Generated by Django 3.2.23 on 2024-01-28 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20240128_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='evidencetypecustomfield',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='evidencetypequalitycontrol',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
