import pytest
from mixer.backend.django import mixer
from ..models import thumbnail_location
pytestmark = pytest.mark.django_db


@pytest.fixture()
def some_product(self, title='Test'):
    obj = mixer.blend('products.product', title=title)
    return obj


class TestProduct:
    def test_model(self):
        obj = mixer.blend('products.product')
        assert obj.pk == 1, 'Should save an instance'

    def test_thumb_location(self):
        obj = mixer.blend('products.thumbnail', product=some_product(self, title='Test product'))
        thumb_loc = thumbnail_location(obj, 'test.jpg')
        assert obj.product.title == 'Test product'
        assert 'test.jpg' in thumb_loc


"""
def thumbnail_location(instance, filename):
    return "products/%s/thumbnails/%s" % (instance.product.slug, filename)
"""