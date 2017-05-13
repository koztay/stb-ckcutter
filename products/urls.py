from django.conf.urls import url

from .views import (
    ProductDetailView,
    ProductListView,
    NewProductListView,
    VariationListView,
    # product_list_by_tag,
    xml_latest,
    xml_test,
    stream_response,
    update_session,
    download_xml_streaming,
    ProductListTagFilterView,
)

urlpatterns = [
    # Examples:
    # url(r'^$', 'newsletter.views.home', name='home'),
    # url(r'^$', product_list, name='products'),
    url(r'^$', NewProductListView.as_view(), name='products'),
    url(r'^(?P<slug>[\w-]+)/$', ProductDetailView.as_view(), name='product_detail'),
    # url(r'^tag/(?P<tag_slug>[-\w]+)/$', product_list_by_tag, name='product_list_by_tag'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', ProductListTagFilterView.as_view(), name='product_list_by_tag'),
    # url(r'^(?P<pk>\d+)/$', ProductDetailView.as_view(), name='product_detail'),
    url(r'^(?P<pk>\d+)/inventory/$', VariationListView.as_view(), name='product_inventory'),
    url(r'^(?P<marketplace>[\w-]+)/istebu.xml', xml_latest, name='products_xml'),
    url(r'^test/(?P<marketplace>[\w-]+)/istebu.xml', xml_test, name='products_test_xml'),
    # url(r'^(?P<id>\d+)', 'products.views.product_detail_view_func', name='product_detail_function'),
    # url(r'^(?P<slug>[\w-]+)/$', 'products.views.detail_slug_view', name='product_detail_slug_function'),
    # url(r'^(?P<slug>[\w-]+)/$', ProductDetailView.as_view(), name='detail_slug'),
    url(r'^stream/stream.xml$', download_xml_streaming, name='stream_xml'),


]
