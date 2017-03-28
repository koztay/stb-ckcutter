from django.db import models


from products.models import Variation


# Create your models here.
class Vendor(models.Model):
    isim = models.CharField(max_length=120, unique=True)
    unvan = models.CharField(max_length=120)
    adres = models.TextField(null=True, blank=True)
    telefon = models.CharField(max_length=120, null=True, blank=True)
    fax = models.CharField(max_length=120, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    vergi_dairesi = models.CharField(max_length=120)
    vergi_no = models.CharField(max_length=120)
    urunler = models.ManyToManyField(Variation, blank=True)  # null=True koyunca aşağıdaki hatayı veriyor:
    # System check identified some issues:
    # WARNINGS:
    # vendors.Tedarikci.urunler: (fields.W340) null has no effect on ManyToManyField.

    def __str__(self):
        return self.unvan
