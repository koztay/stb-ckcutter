from django.conf import settings
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class AdminLocaleURLMiddleware(MiddlewareMixin):

    special_cases = {
        '/admin/': 'en',
        '/istebu_backend_ax476sxc/': 'en',
    }

    def process_request(self, request):
        if request.path_info in self.special_cases:
            request.LANG = getattr(settings, 'ADMIN_LANGUAGE_CODE', settings.LANGUAGE_CODE)
            translation.activate(request.LANG)
            request.LANGUAGE_CODE = request.LANG

    def process_response(self, request, response):
        translation.deactivate()
        return response

