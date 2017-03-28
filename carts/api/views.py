from carts.models import Cart
from .serializers import CartModelSerializer
from rest_framework import generics


class CartItemsListView(generics.ListAPIView):
    serializer_class = CartModelSerializer

    def get_queryset(self):
        cart_id = self.request.session.get("cart_id")
        return Cart.objects.filter(id=cart_id)
