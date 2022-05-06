# Generated by Django 2.1.7 on 2019-12-04 19:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('unit_label_name', models.CharField(max_length=15)),
                ('max_units', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('qty_per_unit', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('active', models.BooleanField(default=True)),
                ('rank', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checkout_time', models.DateTimeField(auto_now_add=True)),
                ('uploaded', models.BooleanField(default=False)),
                ('password_hash', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('checkout_time',),
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units_taken', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='tallyhq.Item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='tallyhq.Order')),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tallyhq.School')),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
            },
        ),
        migrations.CreateModel(
            name='ValidationPassword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digest', models.CharField(max_length=65)),
                ('uploaded_date', models.DateTimeField(auto_now_add=True)),
                ('hash_digest', models.CharField(max_length=65)),
            ],
        ),
        migrations.CreateModel(
            name='Waiver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, default='', upload_to='')),
                ('uploaded_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(related_name='orders', through='tallyhq.OrderItem', to='tallyhq.Item'),
        ),
        migrations.AddField(
            model_name='order',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tallyhq.Teacher', unique_for_month='checkout_time'),
        ),
        migrations.AddField(
            model_name='order',
            name='waiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tallyhq.Waiver'),
        ),
        migrations.AlterUniqueTogether(
            name='order',
            unique_together={('password_hash', 'teacher')},
        ),
    ]
