# Generated by Django 3.2.23 on 2024-01-07 09:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_supplier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('level', models.IntegerField()),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.department')),
            ],
            options={
                'verbose_name': 'Department',
            },
        ),
    ]
