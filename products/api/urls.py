from django.conf.urls import url

from .views import ProductListAPIView, VariationListAPIView, ProductDetailAPIView

urlpatterns = [
    url(r'^variations/$', VariationListAPIView.as_view(), name='api_variation_list'),  # /api/products/variations
    url(r'^$', ProductListAPIView.as_view(), name='api_product_list'),  # /api/products/
    url(r'^(?P<pk>[0-9]+)$', ProductDetailAPIView.as_view(), name='api_detail_view'),
]

