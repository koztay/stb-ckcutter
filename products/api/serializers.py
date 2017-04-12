from rest_framework import serializers

from products.models import Product, Variation


class ProductModelSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product', 'thumbnails', ]

    def get_product(self, obj):
        product_id = obj.pk
        product = Product.objects.get(id=product_id)
        product = {
            'id': product.pk,
            'title': product.title,
        }
        return product

    def get_thumbnails(self, obj):
        product_id = obj.pk
        product = Product.objects.get(id=product_id)

        images = product.productimage_set.all()
        thumbnails_array = []

        for image in images:
            product_image = {
                'main_image': image.get_image_path(),
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


