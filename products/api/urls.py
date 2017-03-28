from django.conf.urls import url

from .views import ProductListAPIView, VariationListAPIView

urlpatterns = [
    url(r'^variations/$', VariationListAPIView.as_view(), name='api_variation_list'),  # /api/products/variations
    # url(r'^$', ProductListAPIView.as_view(), name='api_product_list'),  # /api/products/
    # yuakridaki url 'yi bulamıyor
]


