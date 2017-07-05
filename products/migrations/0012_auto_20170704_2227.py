# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-04 19:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_product_sub_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='remote_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.Product'),
        ),
    ]
