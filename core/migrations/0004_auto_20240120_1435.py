# Generated by Django 3.2.23 on 2024-01-20 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eav', '0010_dynamic_pk_type_for_models'),
        ('core', '0003_evidencetype_attachment_required'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eav.attribute')),
            ],
        ),
        migrations.AddField(
            model_name='evidencetype',
            name='custom_fields',
            field=models.ManyToManyField(to='core.CustomField'),
        ),
    ]
