import pytest
from mixer.backend.django import mixer
from ..models import default_fields
pytestmark = pytest.mark.django_db


class TestProductImportMap:
    def test_init(self):
        obj = mixer.blend('importer.ProductImportMap', name='Deneme Importer Map')
        assert obj.pk == 1, 'Should save an instance'
        assert str(obj) == 'Deneme Importer Map', 'Should return self.name'


class TestFields:
    def test_init(self):
        obj = mixer.blend('importer.Fields', product_field='price', xml_field='fiyat')
        assert obj.pk == 1, 'Should save an instance'
        assert str(obj) == "price - fiyat :", 'Should return product_filed - xml_filed'

    def test_get_xml_filed(self):
        obj = mixer.blend('importer.Fields', product_field='price', xml_field='fiyat')
        assert obj.get_xml_field() == 'fiyat', 'Should return the text of xml_field'

# Aşağıdaki post_save_receiver 'ı nasıl test ederiz bilmiyorum
"""
def import_map_post_save_receiver(sender, instance, *args, **kwargs):
    # print("map_post_save_receiver çalıştı:", sender)  # sender ile instance farklı birbirinden
    # print("instance:", instance)
    # yukarıda tanımlanan default fieldları oluşturuyoruz:
    for field in default_fields:
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
"""