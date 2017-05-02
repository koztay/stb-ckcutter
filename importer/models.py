from django.core.urlresolvers import reverse
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from products.models import AttributeType, ProductType


class XMLFileSystemStorage(FileSystemStorage):

    def __init__(self, xmlpath):
        self.xmlpath = xmlpath
        super(XMLFileSystemStorage, self).__init__(location=os.path.join(settings.STATIC_ROOT, self.xmlpath),
                                                   base_url=settings.STATIC_URL+self.xmlpath)

    def __eq__(self, other):
            return self.xmlpath == other.xmlpath

xmlStorage = XMLFileSystemStorage('xml/upload')

# Create your models here.
# buraya mapping ile ilgili bir model koyabilirim.
# sonuçta her firmanın kendine has bir importer 'ı olacak.


# Eğer ürüne ilişkin hiç attribute yoksa sadece default filed 'lar eşleştirilebiliyor.
# Burada default field 'lar view 'da işlenerek product 'lar ile ya eşleşip update ediliyorlar,
# ya da yeni product yaratılıyor. Aşağıdaki mantıkta ileride istediğimiz kadar field ekleyip çıkartmamız mümkün.
# Ve ekleme çıkarma nericesinde de  kodumuzda değişiklik yapmamız muhtemelen (eğer field foreign key değilse) gerekmez.


# bu map 'e ait bir de file field olmalı aslında ki o file'a ilişkin map olsun bu.
# hatta webden çekiyorsak çektiğimiz url 'yi de field olarak girmeliyiz.
class ProductImportMap(models.Model):

    name = models.CharField(max_length=120,
                            help_text='Import edeceğimiz dosyaya ilişkin isim')
    type = models.CharField(max_length=120, default='Generic Product',
                            null=True, blank=True,
                            help_text='Product Type değeri yazılacak, Örneğin: "Generic Product"')
    root = models.CharField(max_length=120, blank=True, null=True,
                            help_text='Eğer XML dosyası ise o zaman ürünlerin çekileceği root tagi yaz.')
    replace_words = models.TextField(blank=True, null=True)
    dropping_words = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Fields(models.Model):
    """
    import ast
    ast.literal_eval("{'muffin' : 'lolz', 'foo' : 'kitty'}")
    {'muffin': 'lolz', 'foo': 'kitty'}
    
    Yukarıdaki örnekten herhangi bir eşleştirme yapamadığımız yerler için default değer tanımlayabiliriz.
    """
    map = models.ForeignKey(ProductImportMap, blank=True, null=True)
    product_field = models.CharField(max_length=20, blank=True, null=True)  # bizdeki
    #  eşleşeceği field
    xml_field = models.CharField(max_length=1200, blank=True, null=True)  # XML  ya da excel deki field

    def __str__(self):
        return "%s - %s :" % (self.product_field, self.xml_field)

    def get_xml_field(self):
        return "%s" % self.xml_field


class ImporterFile(models.Model):
    """
    This model keeps the file information.
    """
    # import_map = models.OneToOneField(XMLImportMap, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    file = models.FileField(storage=xmlStorage)  # upload_to parametresi olmamalı burada, yoksa upload edemiyor.
    remote_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

    def get_file_path(self):
        # img = self.image
        if self.file and hasattr(self.file, 'url'):
            file_url = self.file.url
            print("before :", file_url)
            # remove STATIC_URL from img_url in our case /static/
            file_url = file_url.replace(settings.STATIC_URL, "/", 1)
            print("after :", file_url)
            # # combine with STATIC_ROOT location in our case /static_root (Trailing slash koyma!!!!!!!!)

            file_path = settings.STATIC_ROOT + file_url  # os.path.join does not joins what the fuck!!!!
            print("file_path :", file_path)

            return file_path
        else:
            return None  # None


# Bu fonksiyon mapteki product_tipine göre fieldları oluşturuyor. Ancak tek excelde birçok product tipinden ürün
# gireceksek o zaman generic import oluşturabiliriz. Sonuçta default olarak product tipi oluşacak ve yukarıdaki
# default fieldlar dönecek. Ürünleri process_row 'da import ederken de tip kategori vb. alanlar set edilecek.
# Ancak product tipi oluşturmuşsak ve feature değerleri belirtmişsek o zaman specific tipte ürün girmeye de imkan
# verecek. Çünkü o zaman da feature 'lara göre fieldları döndürüyor ve eşleştirmeye imkan tanıyor.
def import_map_post_save_receiver(sender, instance, *args, **kwargs):
    # print("map_post_save_receiver çalıştı:", sender)  # sender ile instance farklı birbirinden
    # print("instance:", instance)
    # yukarıda tanımlanan default fieldları oluşturuyoruz:
    for field in settings.DEFAULT_FIELDS:
        if field is not "IGNORE":
            Fields.objects.get_or_create(map=instance, product_field=field)
    # eğer specific bir ürün grubu import edeceksek ve aynı zamanda da featureları da import edeceksek o zaman
    # map oluştururken generic değil de Projeksiyon Cihazı, Perde vb. gibi özel bir tip oluşturuyoruz. O zaman
    # o ürn tipine ilişkin özellik listesini excel ile eşleştirebilelim diye aşağıdaki kod çalışıyor.
    try:
        product_type = ProductType.objects.get(name=instance.type)
        product_features = AttributeType.objects.filter(product_type=product_type)
        for feature in product_features:
            Fields.objects.get_or_create(map=instance, product_field=feature.type)
    except:
        print("böyle bir product tipi yok")
        return False


post_save.connect(import_map_post_save_receiver, sender=ProductImportMap)

