# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 22:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isim', models.CharField(max_length=120, unique=True)),
                ('unvan', models.CharField(max_length=120)),
                ('adres', models.TextField(blank=True, null=True)),
                ('telefon', models.CharField(blank=True, max_length=120, null=True)),
                ('fax', models.CharField(blank=True, max_length=120, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('vergi_dairesi', models.CharField(max_length=120)),
                ('vergi_no', models.CharField(max_length=120)),
                ('urunler', models.ManyToManyField(blank=True, to='products.Variation')),
            ],
        ),
    ]
