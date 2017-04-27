from rest_framework import serializers

from products.models import Product, Variation


class ProductModelSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    variation = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product', 'thumbnails', 'variation']

    def get_product(self, obj):
        product_id = obj.pk
        product = Product.objects.get(id=product_id)

        main_category = product.get_main_category()
        if main_category:
            category = main_category.title
            category_url = main_category.get_absolute_url()
        else:
            category = "No category"
            category_url = None

        product_json = {
            'id': product.pk,
            'title': product.title,
            'description': product.description,
            'kdv': product.kdv,
            'price': product.price,
            'url': product.get_absolute_url(),
            'category': category,
            'category_url': category_url,
        }
        return product_json

    def get_variation(self, obj):
        product_id = obj.pk
        product = Product.objects.get(id=product_id)
        variation = product.variation_set.all()[0]
        # burada ilk variation 'ı alıyoruz ama diğerlerini de
        # alma imkanı var.
        variation_json = {
            'id': variation.id,
            'title': variation.title,
            'price': variation.get_product_price(),
            'sale_price': variation.get_sale_price(),
            'stok': variation.inventory
        }
        return variation_json

    def get_thumbnails(self, obj):
        product_id = obj.pk
        product = Product.objects.get(id=product_id)

        images = product.productimage_set.all()
        thumbnails_array = []

        for image in images:
            product_image = {
                'main_image': image.get_image_path(),
                'hd_thumb': image.hd_thumb,
                'sd_thumb': image.sd_thumb,
                'medium_thumb': image.medium_thumb,
                'micro_thumb': image.micro_thumb,
            }
            thumbnails_array.append(product_image)
        return thumbnails_array


class VariationModelSerializer(serializers.ModelSerializer):
    product = ProductModelSerializer()

    class Meta:
        model = Variation
        fields = ['product', 'price', 'sale_price', "inventory"]


