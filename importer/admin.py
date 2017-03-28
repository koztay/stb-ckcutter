from django.contrib import admin

# Register your models here.
from .models import ProductImportMap, Fields


class FieldsInline(admin.TabularInline):
    # readonly_fields = ('product_field',)
    fields = ('product_field', 'xml_field')
    extra = 0
    model = Fields
    ordering = ('product_field', )


class ProductImportMapAdmin(admin.ModelAdmin):
    # list_display = ['__str__', 'price']
    # prepopulated_fields = {'slug': ('title',)}
    inlines = [
        FieldsInline,
    ]

    class Meta:
        model = ProductImportMap

admin.site.register(ProductImportMap, ProductImportMapAdmin)
