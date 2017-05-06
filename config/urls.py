# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.views.generic import TemplateView
from django.views import defaults as default_views
from carts.views import CartView, ItemCountView, ItemsView, CheckoutView, CheckoutFinalView
from orders.views import (
    AddressSelectFormView,
    UserAddressCreateView,
    OrderList,
    OrderDetail)

from newsletter.views import HomeView, ContactView
from products.views import update_session
# from my_importer.views import xml_upload_view, xml_map_view, TaskRunnerView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),
    # url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
                  url(r'^hakkimizda/$', views.flatpage, {'url': '/hakkimizda/'}, name='hakkimizda'),
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('ecommerce_istebu_cookiecutter.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^blog/', include('blog.urls', namespace='blog')),
    url(r'^products/', include('products.urls', namespace='products')),
    url(r'^categories/', include('products.urls_categories', namespace='categories')),
    url(r'^orders/$', OrderList.as_view(), name='orders'),
    url(r'^orders/(?P<pk>\d+)/$', OrderDetail.as_view(), name='order_detail'),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^api/cart/', include('carts.api.urls', namespace='cart_api')),
    url(r'^api/products/', include('products.api.urls', namespace='products_api')),
    url(r'^cart/count/$', ItemCountView.as_view(), name='item_count'),  # ajax call url
    url(r'^cart/items/$', ItemsView.as_view(), name='items_list'),  # ajax call url
    url(r'^checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^checkout/address/$', AddressSelectFormView.as_view(), name='order_address'),
    url(r'^checkout/address/add/$', UserAddressCreateView.as_view(), name='user_address_create'),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name='checkout_final'),

    # ckeditor
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    # data-importer
    url(r'^data-importer/', include('importer.urls', namespace='importer')),
    url(r'^update_session/$', update_session, name='update_session'),

    # url(r'^xml-upload/$', xml_upload_view, name='xml_upload'),
    # url(r'^xml-map/$', xml_map_view, name='xml_map'),
    # url(r'^run-xml-task/$', TaskRunnerView.as_view(), name='run_xml_task'),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
