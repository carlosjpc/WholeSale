# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-20 00:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Disenador', '0015_auto_20161220_0042'),
        ('ShowRoom', '0013_auto_20161213_2109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment_Conditions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=60)),
                ('credit', models.BooleanField(default=False)),
                ('days_of_credit', models.IntegerField(blank=True, default=0, null=True)),
                ('down_payment', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Show_Room_Employee',
            fields=[
                ('role', models.CharField(choices=[('MG', 'Manager'), ('SE', 'Seller'), ('JR', 'Assistant')], default='JR', max_length=2)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='yo', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('designers', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='po_entry',
            old_name='baseItem',
            new_name='unique_item',
        ),
        migrations.AddField(
            model_name='po',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='po',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Disenador.Collection'),
        ),
        migrations.AddField(
            model_name='po',
            name='shipping_co',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='po',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to=None),
        ),
        migrations.AddField(
            model_name='po',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='po_entry',
            name='qty',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='po',
            name='delivery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Disenador.Delivery'),
        ),
        migrations.AddField(
            model_name='po',
            name='payment_conditions',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ShowRoom.Payment_Conditions'),
        ),
    ]