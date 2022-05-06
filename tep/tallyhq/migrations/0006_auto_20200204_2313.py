# Generated by Django 2.1.7 on 2020-02-05 04:13

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tallyhq', '0005_auto_20200204_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='last_changed_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='school',
            name='last_changed_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
