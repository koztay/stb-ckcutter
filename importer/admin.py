from django.contrib import admin
from django.db import models
# Register your models here.
from django import forms

from .models import ProductImportMap, Fields, ImporterFile


class FieldsInline(admin.TabularInline):
    # readonly_fields = ('product_field',)
    fields = ('product_field', 'xml_field')
    readonly_fields = ('product_field',)
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 40})},
    }
    extra = 0
    model = Fields
    ordering = ('product_field', )

    # class Meta:
    #     model = Fields
    #     widgets = {
    #         'xml_field': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
    #     }


class ProductImportMapAdmin(admin.ModelAdmin):
    # list_display = ['__str__', 'price']
    # prepopulated_fields = {'slug': ('title',)}
    inlines = [
        FieldsInline,
    ]

    class Meta:
        model = ProductImportMap

admin.site.register(ProductImportMap, ProductImportMapAdmin)
admin.site.register(ImporterFile)
