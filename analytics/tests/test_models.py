import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestProductView:

    def test_model(self):
        obj = mixer.blend('analytics.ProductAnalytics',
                          product=mixer.blend('products.Product', title='LG G5 Cep Telefonu'),
                          user=mixer.blend('auth.User'))
        assert obj.pk == 1, 'Should save an instance'
        assert str(obj) == 'LG G5 Cep Telefonu', 'Should return the above title value';

    def test_add_count(self):
        obj = mixer.blend('analytics.ProductAnalytics',
                          product=mixer.blend('products.Product', title='LG G5 Cep Telefonu'),
                          user=mixer.blend('auth.User'))

        obj.add_count()  # 1
        obj.add_count()  # 2
        obj.add_count()  # 3
        obj.add_count()  # 4
        obj.add_count()  # 5
        assert obj.count == 5, 'Should return 5'





