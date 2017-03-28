from django.contrib import admin

# Register your models here.
from .models import XMLImportMap, Fields


class FieldsInline(admin.TabularInline):
    # readonly_fields = ('product_field',)
    fields = ('product_field', 'xml_field')
    extra = 0
    model = Fields
    ordering = ('product_field', )


class XMLImportMapAdmin(admin.ModelAdmin):
    # list_display = ['__str__', 'price']
    # prepopulated_fields = {'slug': ('title',)}
    inlines = [
        FieldsInline,
    ]

    class Meta:
        model = XMLImportMap

admin.site.register(XMLImportMap, XMLImportMapAdmin)