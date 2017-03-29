from django.shortcuts import render

# Create your views here.
default_fields = {
    "Mağaza Kodu": {"model": "Variation", "field": "istebu_product_no"},
    "Kategori": {"model": "Product", "field": "categories"},
    "Alt Kategori": {"model": "Product", "field": "categories"},
    "Ürün Tipi": {"model": "ProductType", "field": "name"},  # product.product_type olarak ekle
    "Ürün Adı": {"model": "Product", "field": "title"},
    "KDV": {"model": "Product", "field": "kdv"},
    "Para Birimi": {"model": "Currency", "field": "name"},  # product.buying_currency olarak ekle
    "Alış Fiyatı": {"model": "Variation", "field": "buying_price"},
    "Satış Fiyatı": {"model": "Variation", "field": "sale_price"},
    "Barkod": {"model": "Variation", "field": "product_barkod"},
    "Kargo": {"model": "", "field": ""},
}

