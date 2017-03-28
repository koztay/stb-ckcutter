from django import forms
from django.forms.models import modelformset_factory

from .models import Variation, Category

CAT_CHOICES = (
    ('electronics', 'Electronics'),
    ('accessories', 'Accessories'),
)


class ProductFilterForm(forms.Form):
    # q = forms.CharField(label='Search', required=False)
    # category_id = forms.ModelMultipleChoiceField(
    #     label='Category',
    #     queryset=Category.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False)
    # aşağıdakini aktif edince not a valid choices hatası veriyor...
    # category_title = forms.ChoiceField(
    #     label='Category',
    #     choices=CAT_CHOICES,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False)
    max_price = forms.DecimalField(decimal_places=2, max_digits=12, required=False)
    min_price = forms.DecimalField(decimal_places=2, max_digits=12, required=False)
    # tag = forms.CharField(required=False)
    # hem kategoriye hem de tag 'e  form olarak gerek yok bu form da. Sonuçta tag listi,
    # object list ten oluşturuyoruz ve taglet tıklandıkça object list daralıyor. Benzer
    # şekilde kategoriler de tıklandıkça daralan bir yapı mı yapmak lazım anlamadım.
    # gittigidiyor, yanlarına ürün sayısı yazıp tıklandıkça artan bir yapı seçmiş.
    # Aslında benzer yapı taglerde de olabilir ama mantıklı değil ki giderek daralması
    # lazım.


class VariationInventoryForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = [
            "price",
            "sale_price",
            "inventory",
            "active",
        ]


VariationInventoryFormSet = modelformset_factory(Variation, form=VariationInventoryForm, extra=0)
