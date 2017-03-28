from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
# Create your models here.

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


class XMLImportMap(models.Model):
    name = models.CharField(max_length=120,
                            help_text='Import edeceğimiz dosyaya ilişkin isim')
    root = models.CharField(max_length=120, blank=True, null=True,
                            help_text='Eğer XML dosyası ise o zaman ürünlerin çekileceği root tagi yaz.')

    map = JSONField("Mapinfo")

    def __str__(self):
        return self.name


class Fields(models.Model):
    map = models.ForeignKey(XMLImportMap, blank=True, null=True)
    product_field = models.CharField(max_length=20, blank=True, null=True)  # bizdeki
    #  eşleşeceği field
    xml_field = models.CharField(max_length=1200, blank=True, null=True)  # XML  ya da excel deki field

    def __str__(self):
        return "%s - %s" % (self.product_field, self.xml_field)


# Bu fonksiyon mapteki product_tipine göre fieldları oluşturuyor. Ancak tek excelde birçok produc tipinden ürün
# gireceksek o zaman generic import oluşturabiliriz. Sonuçta default olarak product tipi oluşacak ve yukarıdaki
# default fieldlar dönecek. Ürünleri process_row 'da import ederken de tip kategori vb. alanlar set edilecek.
# Ancak product tipi oluşturmuşsak ve feature değerleri belirtmişsek o zaman specific tipte ürün girmeye de imkan
# verecek. Çünkü o zaman da feature 'lara göre fieldları döndürüyor ve eşleştirmeye imkan tanıyor.
def import_map_post_save_receiver(sender, instance, *args, **kwargs):
    # print("map_post_save_receiver çalıştı:", sender)  # sender ile instance farklı birbirinden
    # print("instance:", instance)
    # yukarıda tanımlanan default fieldları oluşturuyoruz:
    for field in default_fields:
        Fields.objects.get_or_create(map=instance, product_field=field)
    # eğer specific bir ürün grubu import edeceksek ve aynı zamanda da featureları da import edeceksek o zaman
    # map oluştururken generic değil de Projeksiyon Cihazı, Perde vb. gibi özel bir tip oluşturuyoruz. O zaman
    # o ürn tipine ilişkin özellik listesini excel ile eşleştirebilelim diye aşağıdaki kod çalışıyor.
    # try:
    #     product_type = ProductType.objects.get(name=instance.type)
    #     product_features = AttributeType.objects.filter(product_type=product_type)
    #     for feature in product_features:
    #         Fields.objects.get_or_create(map=instance, product_field=feature.type)
    # except:
    #     print("böyle bir product tipi yok")
    #     return False


post_save.connect(import_map_post_save_receiver, sender=XMLImportMap)

