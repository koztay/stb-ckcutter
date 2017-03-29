from django.contrib import admin

# Register your models here.
from .models import XMLImportMap


class XMLImportMapAdmin(admin.ModelAdmin):
    # list_display = ['__str__', 'price']
    # prepopulated_fields = {'slug': ('title',)}
    class Meta:
        model = XMLImportMap

admin.site.register(XMLImportMap, XMLImportMapAdmin)
