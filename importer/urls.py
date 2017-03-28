from django.conf.urls import url

from .views import (
    # create_import_map,
    # create_fields_for_map,
    # edit_map,
    # ProductImportMapListView,
    # ProductImportMapDetailView,
    # ProductImportMapUpdateView,
    # XLSImporterCreateView,
    # XLSXImporterCreateView,
    # XMLImporterCreateView,
    ImporterHomePageView,
    GenericImporterCreateView,
)

urlpatterns = [
    # Examples:
    # url(r'^$', 'newsletter.views.home', name='home'),
    # url(r'^$', 'products.views.product_list', name='products'),

    # url(r'^$', ProductImportMapListView.as_view(), name='map_list'),
    # # url(r'^(?P<pk>\d+)/edit/$', ProductImportMapUpdateView.as_view(), name='map_update'),
    # url(r'^(?P<pk>\d+)/$', ProductImportMapDetailView.as_view(), name='map_detail'),
    #
    # url(r'^(?P<pk>\d+)/edit/$', edit_map, name="edit_map"),
    # url(r'^new/$', create_import_map, name="create_map"),
    # url(r'^assign-fields/$', create_fields_for_map, name="create_map_success"),

    # aşağıdaki url 'ler ile yukarının örtüşmesi gerek. şimdilik aşağıyı disable edelim.
    url(r'^$', ImporterHomePageView.as_view(), name='product_importer_home'),
    url(r'^import/$', GenericImporterCreateView.as_view(), name='generic_importer'),
    # url(r'^XLS/$', XLSImporterCreateView.as_view(), name='xls_importer'),
    # url(r'^XLSX/$', XLSXImporterCreateView.as_view(), name='xlsx_importer'),
    # url(r'^XML/$', XMLImporterCreateView.as_view(), name='xml_importer'),
]


