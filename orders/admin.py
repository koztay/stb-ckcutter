from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from carts.models import Cart, CartItem

from .models import UserCheckout, UserAddress, Order


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ("order_id",
                       "user",
                       "status",
                       "cart",
                       "billing_address",
                       "shipping_address",
                       "shipping_total_price",
                       "order_total",
                       "items"
                       )

    fields = ("order_id",
              "user",
              "status",
              "cart",
              "billing_address",
              "shipping_address",
              "shipping_total_price",
              "order_total",
              "items"
              )

    list_display = ("order_id", "user", "status", "cart", "order_total")
    list_display_links = ('cart', 'user', )

    class Meta:
        model = Order

    def items(self, obj):
        items = obj.cart.cartitem_set.all()
        # html = format_html_join('\n', "<tr><td<{}</td><td<{}</td><td<{}</td><td<{}</td></tr>",
        #                         ((item.product.title, item.line_item_total, item.quantity) for item in items)
        #                         )
        html = format_html_join(
            '\n', "<tr><td>{}</td><td>{}</td><td>{}</td></tr>",
            ((cartitem.item.product.title, cartitem.quantity, cartitem.item.get_sale_price()) for cartitem in items)
        )
        table_header = "<tr><th>Ürün</th><th>Adet</th><th>Satış Fiyatı</th></tr>"
        # tax_total = format_html("<tr><td></td><td>KDV Toplamı :</td><td>{}</td></tr>", obj.cart.tax_total)
        order_total = format_html("<tr><td></td><td>Sipariş Toplamı :</td><td>{}</td></tr>", obj.cart.total)
        final_html = "<table>" + table_header + html + order_total + "</table>"
        return mark_safe(str(final_html))

"""
format_html_join(
    '\n', "<li>{} {}</li>",
    ((u.first_name, u.last_name) for u in users)
)

format_html("{} <b>{}</b> {}",
            mark_safe(some_html), some_text, some_other_text)
"""



admin.site.register(UserCheckout)

admin.site.register(UserAddress)

admin.site.register(Order, OrderAdmin)



"""
    status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
    cart = models.ForeignKey(Cart)
    user = models.ForeignKey(UserCheckout, null=True)
    billing_address = models.ForeignKey(UserAddress, related_name='billing_address', null=True)
    shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', null=True)
    shipping_total_price = models.DecimalField(max_digits=50, decimal_places=2, default=5.99)
    order_total = models.DecimalField(max_digits=50, decimal_places=2, )
    order_id = models.CharField(max_length=50, null=True, blank=True)

class CartItemInline(admin.TabularInline):
    readonly_fields = ('product', 'quantity', 'line_item_total')
    fields = ('product', 'quantity', 'line_item_total', )
    # list_display = ('product', )
    model = CartItem
    extra = 0

    def product(self, obj):
        return obj.item.product.title


class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'no_of_items', 'total']

    inlines = [
        CartItemInline
    ]

    class Meta:
        model = Cart

    def queryset(self, request):
        # Prefetch related objects
        return super(CartAdmin, self).queryset(request).select_related('product')

    def no_of_items(self, obj):
        return str(obj.items.count()) + " ürün"

"""
