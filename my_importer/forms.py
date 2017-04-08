from django import forms
from .models import ImporterFile, XMLImportMap


PRODUCT_FIELD_CHOICES = (
    ("IGNORE", "Ignore This Field"),
    ("Magaza_Kodu", "Mağaza Kodu"),
    ("Kategori", "Kategori"),
    ("Alt_Kategori", "Alt Kategori"),
    ("Urun_Tipi", "Ürün Tipi"),
    ("Urun_Adi", "Ürün Adı"),
    ("Aciklama", "Ürün Açıklaması"),
    ("Stok", "Stok Adedi"),
    ("KDV", "KDV"),
    ("Para_Birimi", "Para Birimi"),
    ("Alis_Fiyati", "Alış Fiyatı"),
    ("Satis_Fiyati", "Satış Fiyatı"),
    ("Barkod", "Barkod"),
    ("Kargo", "Kargo"),
    ("Urun_Resmi", "Ürün Resmi"),

)


class XMLFileSelectionForm(forms.Form):
    """
    This forms selects the source XML file to be imported. After selection associated view must upload the file
    to server and analyze the file structure nodes etc. 
    """
    file = forms.FileField()


class XMLFileMappingForm(forms.Form):
    """
    This form is used for mapping the fields between local product model and uploded xml file. Local data is also
    available in the views.py file as a dictionary. 
    """
    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra')
        # local_choices = kwargs.pop('local_fields')
        super(XMLFileMappingForm, self).__init__(*args, **kwargs)

        for i, xml_field in enumerate(extra):
            # self.fields['custom_%s' % i] = forms.CharField(label=xml_field)
            self.fields['custom_%s' % i] = forms.ChoiceField(label=xml_field, choices=PRODUCT_FIELD_CHOICES)

    def extra_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('custom_'):
                yield (self.fields[name].label, value)


class ImporterFileForm(forms.ModelForm):
    class Meta:
        model = ImporterFile
        fields = ('description', 'file', )


class ImporterMapSelectionForm(forms.Form):
    import_map = forms.ModelChoiceField(queryset=XMLImportMap.objects.all())


class ImporterXMLSelectionForm(forms.Form):
    import_map = forms.ModelChoiceField(queryset=ImporterFile.objects.all())
