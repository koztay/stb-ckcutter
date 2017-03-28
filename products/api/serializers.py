from rest_framework import serializers

from products.models import Product, Variation


class ProductModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['title', 'micro_thumb', 'medium_thumb', 'sd_thumb', 'price', 'kdv']


class VariationModelSerializer(serializers.ModelSerializer):
    product = ProductModelSerializer()

    class Meta:
        model = Variation
        fields = ['product', 'price', 'sale_price']

