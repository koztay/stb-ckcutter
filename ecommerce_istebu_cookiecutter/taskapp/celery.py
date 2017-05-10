
from __future__ import absolute_import
import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings
from kombu import Exchange, Queue

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')  # pragma: no cover


app = Celery('ecommerce_istebu_cookiecutter')

# Aşağıdaki satırları çoklu queue için yazdım.
####################################################################################
app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),  # kur çekme işi için kullanılacak
    Queue('xml',  Exchange('xml_updater'),   routing_key='xml_updater'),  # xml import için kullanılacak
    Queue('images',  Exchange('image_downloader'),   routing_key='image_downloader'),
    # image download işi için kullanılacak
)
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'

task_routes = ('ecommerce_istebu_cookiecutter.taskapp.routers.route_task',)

####################################################################################


class CeleryConfig(AppConfig):
    name = 'ecommerce_istebu_cookiecutter.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object('django.conf:settings')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # pragma: no cover
