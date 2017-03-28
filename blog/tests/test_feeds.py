import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.db


@pytest.fixture
def feed():
    obj1 = mixer.blend('blog.post')
    obj2 = mixer.blend('blog.post')
    obj3 = mixer.blend('blog.post')
    obj4 = mixer.blend('blog.post')
    obj5 = mixer.blend('blog.post')
    obj6 = mixer.blend('blog.post')
    feeds = [obj1, obj2, obj3, obj4, obj5, obj6]
    return feeds


class TestLatestPostsFeed:
    def test_items(self, db):  # db fixture eklemesi test fonksiyonuna parametre olarak oluyormuş...
        obj = feed()
        obj1 = mixer.blend('blog.post')
        assert len(obj) == 6





