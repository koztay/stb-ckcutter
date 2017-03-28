from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CartItemsListView

urlpatterns = [
    url(r'^$', CartItemsListView.as_view(), name='api_cartitems_list'),  # /api/cart/

]

urlpatterns = format_suffix_patterns(urlpatterns)  # bu ne işe yarıyor öğren.
