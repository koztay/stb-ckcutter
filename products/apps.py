from django.apps import AppConfig


class ProductsAppConfig(AppConfig):
    name = 'products'
    verbose_name = 'Products'

    def ready(self):
        # import signal handlers # aşağıdaki satırdaki gibi signals import edilmezse hiçbir
        # signal çalışmıyor...
        # Birşey daha farkettim eğer commit esnasında refactor, vb. gibi checkbox 'ları
        # check ettiysen o zaman geri zekalı pycharm benim şağıda import etiğim satırı
        # siliyor.
        from . import signals