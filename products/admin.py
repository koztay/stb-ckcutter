from django.contrib import admin
# import nested_admin


from .models import (
    Product,
    Variation,
    ProductImage,
    Category,
    ProductFeatured,
    AttributeType,
    AttributeValue,
    ProductType,
    Thumbnail,
    Currency
    )


class VariationInline(admin.StackedInline):
    model = Variation
    # fields = ('title', 'buying_price', 'price', 'sale_price', 'inventory', 'active', )
    # # list_display = ('title', 'buying_currency', 'buying_price', 'price', 'sale_price', 'inventory', 'active',)
    # list_display = ('title', 'buying_currency', )
    extra = 0
    max_num = 10


class AttributeTypeInline(admin.TabularInline):
    model = AttributeType
    extra = 1
    ordering = ("order",)


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    ordering = ("attribute_type__order",)


# class ProductTypeInline(admin.TabularInline):
#     model = ProductType


class AttributeTypeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'product_type', 'order']
    list_editable = ['order']
    fields = ('product_type', 'type', 'product', 'order',)
    ordering = ("product_type", 'order',)
    list_filter = ("product_type",)

    # inlines = [ProductTypeInline, ]  # No ForeignKey Hatası veriyor.
    # exclude = ('product',)

    class Meta:
        model = AttributeType
        order_by = 'order'


class ThumbnailInline(admin.StackedInline):
    extra = 1
    model = Thumbnail


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    max_num = 10
    # inlines = [ThumbnailInline]


class ProductImageAdmin(admin.ModelAdmin):
    search_fields = ['product__title', ]

    inlines = [
        ThumbnailInline,
    ]

    class Meta:
        model = ProductImage


# class ThumbnailInline(nested_admin.NestedStackedInline):
#     model = Thumbnail
#
#
# class ProductImageInline(nested_admin.NestedStackedInline):
#     model = ProductImage
#     inlines = [ThumbnailInline]
#
#
# class ProductImageAdmin(nested_admin.NestedModelAdmin):
#     model = ProductImage
#     inlines = [ThumbnailInline]

# // TODO: Product Search ekle.
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title', ]
    list_display = ['__str__', 'price']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
        ProductImageInline,
        VariationInline,
        AttributeValueInline,
    ]

    class Meta:
        model = Product


class CategoryInline(admin.TabularInline):
    extra = 3
    model = Category
    prepopulated_fields = {'slug': ('title',)}
    verbose_name = "Alt Kategoriler"


class CategoryAdmin(admin.ModelAdmin):
    # list_display = (parent_category, )
    prepopulated_fields = {'slug': ('title',)}

    inlines = [CategoryInline, ]

    class Meta:
        model = Category

    # sadece parent kategorileri liste olarak göstermeye yarıyor.
    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        # categories = Category.objects.filter(parent__in=qs.filter(parent=None))
        # print(categories)
        has_sub = Category.with_childrens.categories_with_children()
        return (qs.filter(parent=None) | has_sub).distinct()


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'updated')
    readonly_fields = ('value', 'updated')


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductFeatured)
admin.site.register(ProductType)
admin.site.register(AttributeType, AttributeTypeAdmin)
admin.site.register(AttributeValue)
admin.site.register(Currency, CurrencyAdmin)

# from .models import TableOfContents, TocArticle, TocSection
#
# class TocArticleInline(nested_admin.NestedStackedInline):
#     model = TocArticle
#     sortable_field_name = "position"
#
# class TocSectionInline(nested_admin.NestedStackedInline):
#     model = TocSection
#     sortable_field_name = "position"
#     inlines = [TocArticleInline]
#
# class TableOfContentsAdmin(nested_admin.NestedModelAdmin):
#     inlines = [TocSectionInline]
#
# admin.site.register(TableOfContents, TableOfContentsAdmin)
