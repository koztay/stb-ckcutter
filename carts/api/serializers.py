from rest_framework import serializers
from carts.models import Cart


class CartModelSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['pk', 'items']

    def get_items(self, obj):
            request = self.context['request']
            card_id = request.session.get("cart_id")
            # or
            card_id = obj.pk
            cart = Cart.objects.get(id=card_id)
            cart_items = cart.cartitem_set.all()
            print(cart_items)
            cart_items_array = []
            for cart_item in cart_items:
                item_in_cart = {
                    'product_id': cart_item.item.product.pk,
                    'product_url': cart_item.item.get_absolute_url(),
                    'product_title': cart_item.item.product.title,
                    'sale_price': cart_item.item.sale_price,
                    'quantity': cart_item.quantity,
                    'sub_total': cart_item.quantity * cart_item.item.sale_price,
                    'image': cart_item.item.product.micro_thumb,
                }
                cart_items_array.append(item_in_cart)
            return cart_items_array
