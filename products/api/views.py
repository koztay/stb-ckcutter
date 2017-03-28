from rest_framework import generics

from products.models import Product
from carts.models import Cart
from .serializers import ProductModelSerializer, VariationModelSerializer


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductModelSerializer

    def get_queryset(self):
        # cart_id = self.request.session.get("cart_id")
        return Product.objects.all()


class VariationListAPIView(generics.ListAPIView):
    serializer_class = VariationModelSerializer

    def get_queryset(self):
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            cart_items = None
        else:
            cart = Cart.objects.get(id=cart_id)
            cart_items = cart.items.all()
        # cart_id = self.request.session.get("cart_id")
        return cart_items
