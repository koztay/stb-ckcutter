# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fields',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('product_field', models.CharField(max_length=20, blank=True, null=True)),
                ('xml_field', models.CharField(max_length=1200, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImportMap',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=120, help_text='Import edeceğimiz dosyaya ilişkin isim')),
                ('type', models.CharField(max_length=120, blank=True, default='Generic Product', null=True, help_text='Product Type değeri yazılacak, Örneğin: "Generic Product"')),
                ('root', models.CharField(max_length=120, blank=True, null=True, help_text='Eğer XML dosyası ise o zaman ürünlerin çekileceği root tagi yaz.')),
            ],
        ),
        migrations.AddField(
            model_name='fields',
            name='map',
            field=models.ForeignKey(to='importer.ProductImportMap', blank=True, null=True),
        ),
    ]
