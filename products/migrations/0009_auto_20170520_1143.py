# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-20 08:43
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_kargo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='currency',
            options={'verbose_name': 'currency', 'verbose_name_plural': 'currencies'},
        ),
        migrations.AddField(
            model_name='product',
            name='frontpage_grup',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('OC', 'ÖNE ÇIKANLAR'), ('FU', 'FIRSAT ÜRÜNLERİ'), ('KU', 'KAMPANYALI ÜRÜNLER'), ('CS', 'ÇOK SATANLAR'), ('GT', 'GÜNÜN TEKLİFLERİ'), ('HT', 'HAFTANIN ÜRÜNLERİ'), ('DU', 'DİĞER ÜRÜNLER')], max_length=20, null=True),
        ),
    ]