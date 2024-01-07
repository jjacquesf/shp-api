# Generated by Django 3.2.23 on 2024-01-07 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_stateorg'),
    ]

    operations = [
        migrations.CreateModel(
            name='SifUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('stateorg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.stateorg')),
            ],
            options={
                'verbose_name': 'SIF user',
                'verbose_name_plural': 'SIF users',
            },
        ),
    ]
