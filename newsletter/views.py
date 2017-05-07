from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic import TemplateView, FormView

from products.models import ProductFeatured, Product, Category
from visual_site_elements.models import SliderImage, Promotion, HorizontalBanner, Testimonial
from .forms import ContactForm
from products.views import SignupFormView


def get_popular_products(category_slug):
    catg_instance = Category.objects.filter(slug=category_slug)
    return Product.objects.all().filter(categories=catg_instance).filter(variation__inventory__gt=0).order_by("?")[:8]


class HomeView(SignupFormView, TemplateView):
    template_name = 'home.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['featured_image'] = ProductFeatured.objects.filter(active=True).order_by("?").first()
        context['products'] = Product.objects.all().filter(variation__inventory__gt=0).order_by("?")[:16]
        context['products2'] = Product.objects.all().filter(variation__inventory__gt=0).order_by("?")[:8]
        context['sliders'] = SliderImage.objects.all().filter(active=True)
        context['horizontal_banner'] = HorizontalBanner.objects.all().filter(active=True).order_by("?").first()
        context['categories'] = Category.objects.all().filter(active=True).filter(show_on_homepage=True).order_by('order', 'pk')
        context['testimonials'] = Testimonial.objects.filter(active=True).order_by("?")[:3]
        # one_cikanlar, cok_satanlar, aradıklarınıza_benzer_urunler,
        context['one_cikanlar'] = get_popular_products(category_slug="one-cikanlar")
        print("context['one_cikanlar'] ", context['one_cikanlar'])
        context['cok_satanlar'] = get_popular_products(category_slug="cok-satanlar")
        # TODO : bu aşağıdaki için algoritmik bir çözüm bulmak lazım...
        context['aradıklarınıza_benzerler'] = get_popular_products(category_slug="aradiklariniza-benzerler")

        # sol taraftaki promosyon için rastgele bir promosyon seç:
        promotion_left = Promotion.objects.all().filter(active=True).order_by("?").first()
        try:
            promotions_right = Promotion.objects.all().exclude(id=promotion_left.id).filter(active=True).order_by("?")[:4]
            promotions = (promotion_left, promotions_right)
        except:
            promotions = None
            pass
        context['promotions'] = promotions

        return context



# Artık bu view 'ı her yerde kullanabiliriz.
class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'
    success_url = reverse_lazy('products:products')  # Buraya kendi URL 'sini yazalım.

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)

        title_align_center = False

        context['form'] = self.get_form()
        context['title'] = "Bize Yazın"
        context['title_align_center'] = title_align_center,
        context['section'] = "İletişim"
        return context

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        full_name = form.cleaned_data.get('full_name')
        message = form.cleaned_data.get('message')
        subject = 'Site Contact Form'
        # from_email = settings.EMAIL_HOST_USER
        from_email = "info@karnas.com.tr"
        to_email = [from_email, 'koztay@me.com']
        contact_message = '%s: %s via %s' % (full_name, message, email)

        send_mail(subject,
                  contact_message,
                  from_email,
                  to_email,
                  fail_silently=True)
        return super(ContactView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)


def contact(request):
    title = "Bize Yazın"
    title_align_center = False

    contact_form = ContactForm(request.POST or None)
    if contact_form.is_valid():
        email = contact_form.cleaned_data.get('email')
        full_name = contact_form.cleaned_data.get('full_name')
        message = contact_form.cleaned_data.get('message')
        subject = 'Site Contact Form'
        from_email = settings.EMAIL_HOST_USER
        to_email = [from_email, 'koztay@me.com']
        contact_message = '%s: %s via %s' % (full_name, message, email)

        send_mail(subject,
                  contact_message,
                  from_email,
                  to_email,
                  fail_silently=True)

        '''
        Yukarıdakinin daha python tarzında yapılış şekli şöyle:
        Sebebi de formda bir sürü field varsa tek tek yazmak
        doğru değil

        for key in form.cleaned_data:
        print(key)
        print(form.cleaned_data.get(key))

        '''

        '''
        bir başka ve daha kısa yöntem de şu:
        python 2.7 'de:
        from.cleaned_data.iteritems() imiş...

        for key, value in form.cleaned_data.items():
        print (key, value)
        '''
    context = {
        'contact_form': contact_form,
        'title': title,
        'title_align_center': title_align_center,
        'section': "İletişim",

    }

    return render(request, "contact.html", context)
