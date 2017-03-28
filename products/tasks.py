from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task

from utils import kur_cek, delete_problematic_images
from .models import Currency


@task(name="sum_two_numbers")
def add(x, y):
    return x + y


@task(name="multiply_two_numbers")
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total


@task(name="sum_list_numbers")
def xsum(numbers):
    return sum(numbers)


@task(name="EURO_cek")
def euro_cek(currency_name='EURO'):
    kur_value = kur_cek.get(currency_name)
    currency, created = Currency.objects.get_or_create(name='EUR')
    currency.value = kur_value
    currency.save()
    return kur_value


@task(name="USD_cek")
def usd_cek(currency_name='ABD DOLARI'):
    kur_value = kur_cek.get(currency_name)
    currency, created = Currency.objects.get_or_create(name='USD')
    currency.value = kur_value
    currency.save()
    return kur_value


@task(name="image_cleaner")
def delete_images():
    return delete_problematic_images.delete_all()

