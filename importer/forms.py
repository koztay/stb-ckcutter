from django import forms

from my_importer.models import ImporterFile

from .models import ProductImportMap


class ProductImporterMapTypeForm(forms.Form):
    import_map = forms.ModelChoiceField(queryset=ProductImportMap.objects.all())


class ProductXMLImporterMapRootValueForm(forms.Form):
    root = forms.CharField()


class ImporterForm(forms.Form):
    import_map = forms.ModelChoiceField(queryset=ProductImportMap.objects.all())
    import_file = forms.ModelChoiceField(queryset=ImporterFile.objects.all())
    number_of_items_for_testing = forms.IntegerField(required=False)
    download_images = forms.BooleanField(required=False)
    allow_item_creation = forms.BooleanField(required=False)
