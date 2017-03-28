# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(unique=True, default='TL', max_length=10, choices=[('TL', 'TURK LIRASI'), ('USD', 'AMERIKAN DOLARI'), ('EUR', 'EURO')]),
        ),
    ]
