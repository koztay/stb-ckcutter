from rest_framework import serializers
from carts.models import Cart


class CartModelSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['pk', 'items', "grand_total"]

    def get_items(self, obj):
        request = self.context['request']
        # card_id = request.session.get("cart_id")
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
                'sale_price': cart_item.item.get_sale_price(),
                'quantity': cart_item.quantity,
                'sub_total': cart_item.quantity*cart_item.item.get_sale_price(),
                # 'image': cart_item.item.product.micro_thumb,
            }
            # aşağıdaki try blok ajax all'un hata HTTP 500 hatası vermesini engelliyor.
            try:
                item_in_cart['image'] = cart_item.item.product.micro_thumb
            except:
                pass

            cart_items_array.append(item_in_cart)
        return cart_items_array

    def get_grand_total(self, obj):
        card_id = obj.pk
        cart = Cart.objects.get(id=card_id)
        cart_items = cart.cartitem_set.all()
        print(cart_items)
        cart_total = 0
        for cart_item in cart_items:
            cart_total += float(cart_item.quantity*cart_item.item.get_sale_price())
        grand_total = {
            'cart_total': cart_total
            # 'image': cart_item.item.product.micro_thumb,
        }
        return grand_total
