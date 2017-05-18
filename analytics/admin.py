from django.contrib import admin

# Register your models here.
from .models import ProductAnalytics


class ProductAnalyticsAdmin(admin.ModelAdmin):
    raw_id_fields = ('product', )
    search_fields = ['product__title', ]
    list_display = ['__str__', 'count', ]

admin.site.register(ProductAnalytics, ProductAnalyticsAdmin)
