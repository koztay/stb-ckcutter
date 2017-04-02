from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from django.db.models.signals import post_save
# Create your models here.
from .xml_processor import get_root, get_all_elements


class XMLImportMap(models.Model):
    name = models.CharField(max_length=120,
                            help_text='Import edeceğimiz dosyaya ilişkin isim')
    root = models.CharField(max_length=120, blank=True, null=True,
                            help_text='Eğer XML dosyası ise o zaman ürünlerin çekileceği root tagi yaz.')
    remote_url = models.URLField(blank=True, null=True)  # if it is specified it can be used to update prices remotely.
    # //TODO : yukarıdaki remote_url gereksiz silinecek. Ya da aşağıdaki remote_url...
    map = JSONField("Mapinfo")  # to access the Json Object use json_object = json.loads(object.map)

    def __str__(self):
        return self.name


class ImporterFile(models.Model):
    """
    This model keeps the file information.
    """
    import_map = models.OneToOneField(XMLImportMap, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='my_importer/')
    remote_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_file_path(self):
        # img = self.image
        if self.file and hasattr(self.file, 'url'):
            file_url = self.file.url
            # remove MEDIA_URL from img_url
            file_url = file_url.replace(settings.MEDIA_URL, "/", 1)
            # combine with media_root
            file_path = settings.MEDIA_ROOT + file_url
            return file_path
        else:
            return None  # None


# def file_upload_post_save_receiver(sender, instance, created, *args, **kwargs):
#     print("file_post_save_receiver çalıştı")
#     file_path = instance.get_file_path()
#     root = get_root(file_path=file_path)
#     get_all_elements(root=root)
#
#
#
# post_save.connect(file_upload_post_save_receiver, sender=ImporterFile)
