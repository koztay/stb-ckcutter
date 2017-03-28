from django import forms


from .models import ProductImportMap


class ProductImporterMapTypeForm(forms.Form):
    import_map = forms.ModelChoiceField(queryset=ProductImportMap.objects.all())


class ProductXMLImporterMapRootValueForm(forms.Form):
    root = forms.CharField()

