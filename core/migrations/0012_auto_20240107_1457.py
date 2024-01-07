# Generated by Django 3.2.23 on 2024-01-07 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_department_parent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'verbose_name': 'SHP Department', 'verbose_name_plural': 'SHP Departments'},
        ),
        migrations.AlterField(
            model_name='department',
            name='level',
            field=models.IntegerField(default=0),
        ),
    ]