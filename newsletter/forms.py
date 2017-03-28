from django import forms
from .models import SignUp


# This is not a contact form and has nothing related with any model
class ContactForm(forms.Form):
    full_name = forms.CharField(label='İsminiz', required=False,)
    email = forms.EmailField(label='E-Posta Adresiniz')
    message = forms.CharField(label='Mesajınız', widget=forms.Textarea)


# class SignUpForm(forms.Form):
#     email = forms.EmailField(label='')
#
#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         return email


# This is a model form
class SignUpForm(forms.ModelForm):
    # Aşağıdaki 3 satırı label göstermesin diye yazdık ama çalışmıyor.
    class Meta:
        model = SignUp
        fields = ['email']

        # exclude = ['full_name'] Bunu hiç kullanma

    """
    Form validation için aşağıdaki fonksiyonu override edeceğiz.
    Bu override ile istediğimiz şekilde form handling yapabileceğiz.
    Yani mükerrer e-mail girişini engellemek gibi mesela.
    """

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # make some validations here
        # email_base, provider = email.split('@')
        # domain, extension = provider.split('.')  # eğer birden fazla nokta varsa hata veriyor.
        #
        # # if not domain == 'USC':
        # # raise forms.ValidationError("Please make sure you use your USC email")
        #
        # if not extension == "edu":
        #     raise forms.ValidationError("Please use a valid .edu email address")

        return email

        # def clean_full_name(self):
        #     full_name = self.cleaned_data.get('full_name')
        #     # write validaton code here if necessary.
        #     return full_name

