# Generated by Django 3.2.23 on 2024-01-28 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20240128_2130'),
    ]

    operations = [
        migrations.RenameField(
            model_name='evidencefinding',
            old_name='description',
            new_name='comments',
        ),
    ]