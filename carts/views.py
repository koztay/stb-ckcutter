# import braintree
import json
from requests import Request, Session
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin


from orders.forms import GuestCheckoutForm
from orders.mixins import CartOrderMixin
from orders.models import UserCheckout
from products.models import Variation
from .models import Cart, CartItem


if settings.DEBUG:  # bunu DEBUG 'a bağlamak doğru mu acaba? Sıkıntı gözükmüyor.
    print('CHECKOUT yapıyorum DEBUG=True')
    api_url = settings.PAYNET_TEST_API_URL
    paynet_js_url = settings.PAYNET_TEST_PAYNETJS_URL
else:
    print('CHECKOUT yapıyorum DEBUG=False')
    api_url = settings.PAYNET_PRODUCTION_API_URL
    paynet_js_url = settings.PAYNET_PRODUCTION_PAYNETJS_URL

print("carts.views içerisindeki bu printleri neden yazıyor bu? Ayrıca debug değerini neden doğru okumaz?")
print('PAYNET_PUBLISHABLE_KEY: ', settings.PAYNET_PUBLISHABLE_KEY)
print('PAYNET_SECRET_KEY: ', settings.PAYNET_SECRET_KEY)
print('PAYNET_TEST_API_URL: ', settings.PAYNET_TEST_API_URL)
print('PAYNET_TEST_PAYNETJS_URL: ', settings.PAYNET_TEST_PAYNETJS_URL)
print('PAYNET_PRODUCTION_API_URL: ', settings.PAYNET_PRODUCTION_API_URL)
print('PAYNET_PRODUCTION_PAYNETJS_URL: ', settings.PAYNET_PRODUCTION_PAYNETJS_URL)


class ItemCountView(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get("cart_id")
            if cart_id is None:
                count = 0
            else:
                cart = Cart.objects.get(id=cart_id)
                count = cart.items.count()
            request.session["cart_item_count"] = count
            return JsonResponse({"count": count})
        else:
            raise Http404


class ItemsView(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get("cart_id")
            if cart_id is None:
                cart_items = None
            else:
                cart = Cart.objects.get(id=cart_id)
                cart_items = cart.items.all()
                print(cart_items)
                for cart_item in cart_items:
                    print('cart item title', cart_item.product.title)
                    # print('cart item image', cart_item.item.product.productimage_set[0])
                    # burada pk 'den product ve image 'a nasıl erişeceğiz?

                cart_items = serializers.serialize('json', cart.items.all(), fields=('product', 'sale_price'))
            return JsonResponse({"cart_items": cart_items})
        else:
            raise Http404


class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = "carts/view.html"

    def get_object(self, *args, **kwargs):
        self.request.session.set_expiry(0)  # 5 minutes
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            cart = Cart()
            cart.tax_percentage = 0.075  # TODO: bunu üründen al.
            cart.save()
            cart_id = cart.id
            self.request.session["cart_id"] = cart_id
        cart = Cart.objects.get(id=cart_id)
        if self.request.user.is_authenticated():
            cart.user = self.request.user
            cart.save()
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        item_id = request.GET.get("item")
        delete_item = request.GET.get("delete", False)
        flash_message = ""
        item_added = False

        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            qty = request.GET.get("qty", 1)
            try:
                if int(qty) < 1:
                    delete_item = True
            except:
                raise Http404

            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)

            if created:
                flash_message = "Ürün sepetinize eklendi."
                item_added = True
            if delete_item:
                flash_message = "Ürün sepetinizden çıkarıldı."
                cart_item.delete()
            else:
                if not created:
                    flash_message = "Ürün adeti güncellendi."
                cart_item.quantity = qty
                cart_item.save()
            if not request.is_ajax():
                return HttpResponseRedirect(reverse("cart"))
                # return cart_item.cart.get_absolute_url()

        if request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total = None
            try:
                subtotal = cart_item.cart.subtotal
            except:
                subtotal = None

            try:
                cart_total = cart_item.cart.total
            except:
                cart_total = None

            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = None

            try:
                total_items = cart_item.cart.items.count()
            except:
                total_items = 0

            data = {
                "quantity": qty,
                "deleted": delete_item,
                "item_added": item_added,
                "line_total": total,
                "subtotal": subtotal,
                "cart_total": cart_total,
                "tax_total": tax_total,
                "flash_message": flash_message,
                "total_items": total_items
            }

            return JsonResponse(data)

        context = {
            "object": self.get_object()
        }
        template = self.template_name
        return render(request, template, context)


class CheckoutView(CartOrderMixin, FormMixin, DetailView):
    model = Cart
    template_name = "carts/checkout_view.html"
    form_class = GuestCheckoutForm

    def get_object(self, *args, **kwargs):
        cart = self.get_cart()
        if cart is None:
            return None
        return cart

    def get_context_data(self, *args, **kwargs):
        context = super(CheckoutView, self).get_context_data(*args, **kwargs)
        user_can_continue = False
        user_check_id = self.request.session.get("user_checkout_id")
        if self.request.user.is_authenticated():
            user_can_continue = True
            user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)
            user_checkout.user = self.request.user
            user_checkout.save()
            context["client_token"] = user_checkout.get_client_token()
            self.request.session["user_checkout_id"] = user_checkout.id
        elif not self.request.user.is_authenticated() and user_check_id is None:
            context["login_form"] = AuthenticationForm()
            context["next_url"] = self.request.build_absolute_uri()
        else:
            pass

        if user_check_id is not None:
            user_can_continue = True
            if not self.request.user.is_authenticated():  # GUEST USER
                user_checkout_2 = UserCheckout.objects.get(id=user_check_id)
                context["client_token"] = user_checkout_2.get_client_token()

        # if self.get_cart() is not None:
        context["order"] = self.get_order()
        context["user_can_continue"] = user_can_continue
        context["form"] = self.get_form()
        context["paynet_js_url"] = paynet_js_url
        context["paynet_publishable_key"] = settings.PAYNET_PUBLISHABLE_KEY

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user_checkout, created = UserCheckout.objects.get_or_create(email=email)
            request.session["user_checkout_id"] = user_checkout.id
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("checkout")

    def get(self, request, *args, **kwargs):
        get_data = super(CheckoutView, self).get(request, *args, **kwargs)
        cart = self.get_object()
        if cart is None:
            return redirect("cart")
        new_order = self.get_order()
        user_checkout_id = request.session.get("user_checkout_id")
        if user_checkout_id is not None:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            if new_order.billing_address is None or new_order.shipping_address is None:
                return redirect("order_address")
            new_order.user = user_checkout
            new_order.save()
        return get_data


class CheckoutFinalView(CartOrderMixin, View):

    def post(self, request, *args, **kwargs):
        order = self.get_order()
        order_total = order.order_total
        nonce = request.POST.get("payment_method_nonce")
        session_id = request.POST.get("session_id")
        token_id = request.POST.get("token_id")
        print("session_id : ", session_id)
        print("token_id : ", token_id)
        print("eğer bu değerler varsa o zaman transaction yapabiliriz...")

        if session_id is not None and token_id is not None:
            headers = {"Content-Type": "application/json; charset=UTF-8",
                       "Accept": "application/json; charset=UTF-8",
                       "Authorization": settings.PAYNET_SECRET_KEY
                       }
            data = {
                'session_id': session_id,
                'token_id': token_id,
                "reference_no": "1234",
                "transaction_type": '1'
                }

            print('headers: ', headers)
            print('data :', data)
            # yukarıdaki token_id değerinden PAYNET bizim ne kadar charge ettiğimizi biliyor.
            # // TODO: reference no oluşturmamız lazım, kendi sistemimize göre.

            final_api_url = api_url + "/v1/transaction/charge"
            result = requests.post(final_api_url, json=data, headers=headers)
            json_response = result.json()
            print("json_response", json_response)

            if 'is_succeed' in json_response:
                # şimdilik sadece print edip gelen değerleri kontrol edelim
                if json_response['is_succeed']:
                    # result.transaction.id to order
                    order.mark_completed(order_id=json_response['order_id'])
                    messages.success(request, "Siparişiniz için teşekkür ederiz.")
                    # burada siliyoruz cart değerlerini
                    del request.session["cart_id"]
                    del request.session["order_id"]
                else:
                    # messages.success(request, "There was a problem with your order.")
                    # Unauthorized Credential hatası verdiği yer burası:
                    messages.error(request, "%s" % (json_response['message']))
                    return redirect("checkout")
            else:
                # messages.success(request, "There was a problem with your order.")
                messages.success(request, "%s" % (json_response['message']))
                return redirect("checkout")
        else:
            print("form post edildikten sonra nonce değerini bulamadık ve cartı silemedik.")
        return redirect("order_detail", pk=order.pk)

    def get(self, request, *args, **kwargs):
        return redirect("checkout")

