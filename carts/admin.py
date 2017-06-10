from django.contrib import admin

from .models import Cart, CartItem


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


admin.site.register(Cart, CartAdmin)



"""

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title', 'istebu_product_no']
    list_display = ['__str__', 'istebu_product_no', 'price', 'sale_price', 'stok', 'active', 'frontpage_grup',
                    'updated']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['active', 'frontpage_grup']
    list_filter = (StokListFilter, CategoriesListFilter)
    inlines = [
        ProductImageInline,
        VariationInline,
        AttributeValueInline,
    ]

    class Meta:
        model = Product

    def sale_price(self, obj):
        return obj.variation_set.all()[0].sale_price

    def stok(self, obj):
        return obj.variation_set.all()[0].inventory

    def queryset(self, request):
        # Prefetch related objects
        return super(ProductAdmin, self).queryset(request).select_related('variation')



"""
