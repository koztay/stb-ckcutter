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

admin.site.empty_value_display = '???'


class StokListFilter(admin.SimpleListFilter):

    """
    This filter will always return a subset of the instances in a Model, either filtering by the
    user choice or by a default value.
    """
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Stok VAR / YOK'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'stok_miktari'

    default_value = None

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_of_lookups = [(0, "Stokta YOK"), (1, "Stokta VAR")]
        return sorted(list_of_lookups, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            print("value :", self.value())
            if int(self.value()) == 0:
                return queryset.filter(variation__inventory=self.value())
            else:
                return queryset.filter(variation__inventory__gt=0)
        return queryset

    def value(self):
        """
        Overriding this method will allow us to always have a default value.
        """
        value = super(StokListFilter, self).value()
        if value is None:
            if self.default_value is None:
                self.default_value = 1
            else:
                value = self.default_value
        return str(value)


class CategoriesListFilter(admin.SimpleListFilter):

    """
    This filter will always return a subset of the instances in a Model, either filtering by the
    user choice or by a default value.
    """
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Kategori'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category'

    default_value = None

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_of_categories = []
        queryset = Category.objects.all()
        for category in queryset:
            list_of_categories.append(
                (str(category.id), category.title)
            )
        return sorted(list_of_categories, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            category_object = Category.objects.get(id=self.value())
            return queryset.filter(categories=category_object)
        return queryset

    def value(self):
        """
        Overriding this method will allow us to always have a default value.
        """
        value = super(CategoriesListFilter, self).value()
        if value is None:
            if self.default_value is None:
                # If there is at least one Species, return the first by name. Otherwise, None.
                first_categories = Category.objects.order_by('title').first()
                value = None if first_categories is None else first_categories.id
                self.default_value = value
            else:
                value = self.default_value
        return str(value)


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
    search_fields = ['product__title', 'thumbnail__width']

    inlines = [
        ThumbnailInline,
    ]

    class Meta:
        model = ProductImage


class ThumbnailAdmin(admin.ModelAdmin):
    list_filter = ('type',)
    search_fields = ['type', 'width', 'height']


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


class CategoryInline(admin.TabularInline):
    extra = 3
    model = Category
    prepopulated_fields = {'slug': ('title',)}
    verbose_name = "Alt Kategoriler"
    ordering = ("title",)


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
admin.site.register(Thumbnail, ThumbnailAdmin)
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
