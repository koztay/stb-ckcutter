from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.flatpages import views

from products.models import ProductFeatured, Product, Category
from visual_site_elements.models import SliderImage, Promotion, HorizontalBanner, Testimonial
from .forms import ContactForm, SignUpForm
from .models import SignUp


# Create your views here.
def home(request):
    title = 'Sign Up Now'

    featured_image = ProductFeatured.objects.filter(active=True).order_by("?").first()
    products = Product.objects.all().order_by("?")[:16]
    products2 = Product.objects.all().order_by("?")[:8]
    sliders = SliderImage.objects.all().filter(active=True)
    horizontal_banner = HorizontalBanner.objects.all().filter(active=True).order_by("?").first()
    categories = Category.objects.all().filter(active=True).filter(show_on_homepage=True).order_by('order', 'pk')
    # sol taraftaki promosyon için rastgele bir promosyon seç:
    promotion_left = Promotion.objects.all().filter(active=True).order_by("?").first()

    # sol taraf için seçilen promosyonu aşağıdaki listeden çıkar ve kalanlar arasından ilk 4 'ü al, rastgele sırala.
    try:
        promotions_right = Promotion.objects.all().exclude(id=promotion_left.id).filter(active=True).order_by("?")[:4]
        promotions = (promotion_left, promotions_right)
    except:
        promotions = None
        pass

    testimonials = Testimonial.objects.filter(active=True).order_by("?")[:3]

    if request.method == "POST":
        form = SignUpForm(request.POST)

        '''
        form = SignUpForm()
        form instance oluştururken parantez içindeki parametreleri
        yazmazsak POST edildiğinde hiçbirşey eklenmiyor database'e.
        '''
        if form.is_valid():
            instance = form.save(commit=False)
            email = form.cleaned_data.get('email')

            # Aynı e-posta ile kayıt olunmuş mu bak
            if SignUp.objects.filter(email=email).exists():
                # daha önce bu email ile kayıt olunmuş
                messages.error(request, 'Bu e-posta ile daha önce kayıt olunmuş!', "danger")
            else:
                # daha önce kayıt olunmamış kaydedebilirsin.
                instance.save()
                messages.success(request, 'Haber bültenimize başarıyla kayıt oldunuz.')

                # try:
                #     sign_upped = SignUp.objects.filter(email=email).exists()
                #     if sign_upped:
                #         messages.error(request, 'Bu e-posta ile daha önce kayıt olunmuş!', "danger")
                #     else:
                #         instance.save()
                #         messages.success(request, 'Haber bültenimize başarıyla kayıt oldunuz.')
                # except:
                #     pass

        else:
            messages.error(request, 'Hatalı e-posta girdiniz.!', "danger")
    else:
        form = SignUpForm()

   # about_us_page = reverse(views.flatpage, kwargs={'url': '/hakkimizda/'})

    context = {
        "title": title,
        "form": form,
        "featured_image": featured_image,
        "products": products,
        "products2": products2,
        "sliders": sliders,
        "promotions": promotions,
        "categories": categories,
        "horizontal_banner": horizontal_banner,
        "testimonials": testimonials,
        # "about_us_page": about_us_page,
    }

    # if form.is_valid():
    #     # form.save()
    #     # print request.POST['email'] #not recommended
    #     instance = form.save(commit=False)
    #
    #     full_name = form.cleaned_data.get("full_name")
    #     if not full_name:
    #         full_name = "New full name"
    #     instance.full_name = full_name
    #     # if not instance.full_name:
    #     # 	instance.full_name = "Justin"
    #     instance.save()
    #     context = {
    #         "title": "Thank you"
    #     }

    return render(request, "home.html", context)


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
# def contact(request):
#     title = 'Contact Us'
#     title_align_center = True
#     form = ContactForm(request.POST or None)
#     if form.is_valid():
#         # for key, value in form.cleaned_data.iteritems():
#         # 	print key, value
#         # 	#print form.cleaned_data.get(key)
#         form_email = form.cleaned_data.get("email")
#         form_message = form.cleaned_data.get("message")
#         form_full_name = form.cleaned_data.get("full_name")
#         # print email, message, full_name
#         subject = 'Site contact form'
#         from_email = settings.EMAIL_HOST_USER
#         to_email = [from_email, 'youotheremail@email.com']
#         contact_message = "%s: %s via %s" % (
#             form_full_name,
#             form_message,
#             form_email)
#         some_html_message = """
#         <h1>hello</h1>
#         """
#         send_mail(subject,
#                   contact_message,
#                   from_email,
#                   to_email,
#                   html_message=some_html_message,
#                   fail_silently=True)
#
#     context = {
#         "form": form,
#         "title": title,
#         "title_align_center": title_align_center,
#     }
#     return render(request, "forms.html", context)
