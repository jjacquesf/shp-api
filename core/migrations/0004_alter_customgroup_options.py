# Generated by Django 3.2.23 on 2024-01-04 23:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_customgroup'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customgroup',
            options={'verbose_name': 'Group', 'verbose_name_plural': 'Groups'},
        ),
    ]