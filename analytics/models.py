from django.conf import settings
from django.db import models

# Create your models here.

from products.models import Product


class ProductAnalytics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    product = models.ForeignKey(Product)
    count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.product.title)

    def add_count(self):
        self.count += 1
        return self.count

