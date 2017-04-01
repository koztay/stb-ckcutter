from django.contrib.postgres.fields import JSONField
from django.db import models
# Create your models here.


class XMLImportMap(models.Model):
    name = models.CharField(max_length=120,
                            help_text='Import edeceğimiz dosyaya ilişkin isim')
    root = models.CharField(max_length=120, blank=True, null=True,
                            help_text='Eğer XML dosyası ise o zaman ürünlerin çekileceği root tagi yaz.')
    remote_url = models.URLField(blank=True, null=True)  # if it is specified it can be used to update prices remotely.

    map = JSONField("Mapinfo")

    def __str__(self):
        return self.name
