# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0002_auto_20170226_2115'),
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAnalytics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('count', models.IntegerField(default=0)),
                ('product', models.ForeignKey(to='products.Product')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='productview',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productview',
            name='user',
        ),
        migrations.DeleteModel(
            name='ProductView',
        ),
    ]
