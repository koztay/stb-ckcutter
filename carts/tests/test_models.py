import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db


class TestCart:
    def test_init(self):
        obj = mixer.blend('carts.Cart')
        assert obj.pk == 1, 'Should save an instance'
        assert str(obj) == '1', 'Should return the id'


class TestCartItem:
    def test_init(self):
        obj = mixer.blend('carts.CartItem',
                          cart=mixer.blend('carts.Cart'),
                          item=mixer.blend('products.Variation', price=19.99, title='Default'))
        assert obj.pk == 1, 'Should save an instance'
        assert str(obj) == 'Default', 'Should return the item title'

    def test_remove(self):
        obj = mixer.blend('carts.CartItem',
                          cart=mixer.blend('carts.Cart'),
                          item=mixer.blend('products.Variation', price=19.99, title='Default'))
        result = obj.remove()
        assert 'delete=True' in result, 'Should return an url containing delete keyword'
