from django.contrib import admin
from .models import Vendor
# Register your models here.


class VendorAdmin(admin.ModelAdmin):
    fields = ('isim', 'unvan', 'adres', 'telefon', 'fax', 'email', 'vergi_dairesi', 'vergi_no',)
    # product 'ı vendor eklerken görmek istemiyorum.
    list_display = ['unvan', 'telefon', 'email', ]

admin.site.register(Vendor, VendorAdmin)
