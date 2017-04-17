# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-17 14:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import visual_site_elements.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20170417_1723'),
        ('visual_site_elements', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorizontalTopBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('image', models.ImageField(upload_to=visual_site_elements.models.image_upload_to)),
                ('url', models.CharField(max_length=250)),
                ('active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Category')),
            ],
        ),
        migrations.AlterField(
            model_name='sliderimage',
            name='campaign',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='sliderimage',
            name='sub_title',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]
