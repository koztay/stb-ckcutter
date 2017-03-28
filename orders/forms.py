from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .models import UserAddress

User = get_user_model()


class GuestCheckoutForm(forms.Form):
    email = forms.EmailField()
    email2 = forms.EmailField(label='Verify Email')

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")

        if email == email2:
            user_exists = User.objects.filter(email=email).count()
            if user_exists != 0:
                raise forms.ValidationError("This User already exists. Please login instead.")
            return email2
        else:
            raise forms.ValidationError("Please confirm emails are the same")


class AddressForm(forms.Form):
    billing_address = forms.ModelChoiceField(
        label='Fatura Adresi :',
        queryset=UserAddress.objects.filter(type="billing"),
        widget=forms.RadioSelect,
        empty_label=None
    )
    shipping_address = forms.ModelChoiceField(
        label='Sevk Adresi :',
        queryset=UserAddress.objects.filter(type="shipping"),
        widget=forms.RadioSelect,
        empty_label=None,

    )


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'street',
            'city',
            'state',
            'zipcode',
            'type'
        ]
        labels = {
            'street': _('Cadde, Sokak, Mahalle'),
            'city': _('İl:'),
            'state': _('İlçe:'),
            'zipcode': _('Posta Kodu:'),
            'type': _('Adres Tipi:')
        }


'''
from django.utils.translation import ugettext_lazy as _

class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ('name', 'title', 'birth_date')
        labels = {
            'name': _('Writer'),
        }
        help_texts = {
            'name': _('Some useful help text.'),
        }
        error_messages = {
            'name': {
                'max_length': _("This writer's name is too long."),
            },
        }
'''