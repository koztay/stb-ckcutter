# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import products.models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('type', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.CharField(max_length=120, default='')),
                ('attribute_type', models.ForeignKey(to='products.AttributeType')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(unique=True, max_length=120)),
                ('slug', models.SlugField(unique=True, blank=True, max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('show_on_homepage', models.BooleanField(default=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(to='products.Category', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='TURK LIRASI', max_length=10)),
                ('updated', models.DateField(auto_now=True)),
                ('value', models.FloatField(default=1.0)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=1000)),
                ('description', tinymce.models.HTMLField(default='<h1>default description</h1>', null=True, blank=True)),
                ('price', models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=20)),
                ('active', models.BooleanField(default=True)),
                ('slug', models.SlugField(unique=True, blank=True, max_length=1000)),
                ('show_on_homepage', models.BooleanField(default=True)),
                ('show_on_popular', models.BooleanField(default=True)),
                ('kdv', models.FloatField(default=18.0)),
                ('desi', models.IntegerField(default=1)),
                ('categories', models.ManyToManyField(to='products.Category', blank=True)),
                ('default', models.ForeignKey(related_name='default_category', blank=True, null=True, to='products.Category')),
            ],
            options={
                'ordering': ['-title'],
            },
        ),
        migrations.CreateModel(
            name='ProductFeatured',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('image', models.ImageField(upload_to=products.models.image_upload_to_featured, max_length=2000)),
                ('title', models.CharField(max_length=120, blank=True, null=True)),
                ('text', models.CharField(max_length=220, blank=True, null=True)),
                ('text_right', models.BooleanField(default=False)),
                ('text_css_color', models.CharField(max_length=6, blank=True, null=True)),
                ('show_price', models.BooleanField(default=False)),
                ('make_image_background', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('image', models.ImageField(upload_to=products.models.image_upload_to, max_length=1000, blank=True, null=True)),
                ('product', models.ForeignKey(to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=120, default='Generic Product')),
            ],
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('type', models.CharField(max_length=20, default='hd', choices=[('hd', 'HD'), ('sd', 'SD'), ('medium', 'Medium'), ('micro', 'Micro')])),
                ('height', models.CharField(max_length=20, blank=True, null=True)),
                ('width', models.CharField(max_length=20, blank=True, null=True)),
                ('media', models.ImageField(upload_to=products.models.thumbnail_location, width_field='width', null=True, blank=True, height_field='height', max_length=2000)),
                ('main_image', models.ForeignKey(to='products.ProductImage')),
                ('product', models.ForeignKey(to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('active', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=120)),
                ('price', models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=20)),
                ('buying_price', models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=20)),
                ('buying_price_tl', models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=20)),
                ('sale_price', models.DecimalField(decimal_places=2, blank=True, null=True, max_digits=20)),
                ('inventory', models.IntegerField(blank=True, null=True)),
                ('product_barkod', models.CharField(max_length=100, blank=True, null=True)),
                ('istebu_product_no', models.CharField(max_length=100, blank=True, null=True)),
                ('buying_currency', models.ForeignKey(to='products.Currency', blank=True, null=True)),
                ('product', models.ForeignKey(to='products.Product', blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='productfeatured',
            name='product',
            field=models.ForeignKey(to='products.ProductImage'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(to='products.ProductType', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='product',
            field=models.ForeignKey(to='products.Product', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attributetype',
            name='product',
            field=models.ManyToManyField(to='products.Product', blank=True),
        ),
        migrations.AddField(
            model_name='attributetype',
            name='product_type',
            field=models.ForeignKey(to='products.ProductType'),
        ),
    ]
