# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('isim', models.CharField(unique=True, max_length=120)),
                ('unvan', models.CharField(max_length=120)),
                ('adres', models.TextField(blank=True, null=True)),
                ('telefon', models.CharField(max_length=120, blank=True, null=True)),
                ('fax', models.CharField(max_length=120, blank=True, null=True)),
                ('email', models.EmailField(max_length=254, blank=True, null=True)),
                ('vergi_dairesi', models.CharField(max_length=120)),
                ('vergi_no', models.CharField(max_length=120)),
                ('urunler', models.ManyToManyField(to='products.Variation', blank=True)),
            ],
        ),
    ]
