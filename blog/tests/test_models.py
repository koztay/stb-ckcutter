import pytest
from mixer.backend.django import mixer
from .. import feeds
pytestmark = pytest.mark.django_db


class TestPost:
    def test_init(self):
        obj = mixer.blend('blog.Post', title='Bir varmış bir yokmuş.')
        assert obj.pk == 1, 'Should save an instance'
        assert str(obj) == 'Bir varmış bir yokmuş.', 'Should return self.title'

    def test_get_absolute_url(self):
        obj = mixer.blend('blog.Post', title='Bir varmış bir yokmuş.')
        assert obj.get_absolute_url() is not None, 'should return an url'


class TestComment:
    def test_init(self):
        obj = mixer.blend('blog.Comment', name='kemal',
                          post=mixer.blend('blog.Post', title='House of cards'))
        assert obj.pk == 1, 'Should save an instance'
        assert str(obj) == 'Comment by kemal on House of cards', \
            "Should return : 'Comment by {} on {}'.format(self.name, self.post)."







