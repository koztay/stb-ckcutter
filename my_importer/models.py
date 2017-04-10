from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from django.core.files.storage import FileSystemStorage
import os


class XMLFileSystemStorage(FileSystemStorage):

    def __init__(self, xmlpath):
        self.xmlpath = xmlpath
        super(XMLFileSystemStorage, self).__init__(location=os.path.join(settings.STATIC_ROOT, self.xmlpath),
                                                   base_url=settings.STATIC_URL+self.xmlpath)

    def __eq__(self, other):
            return self.xmlpath == other.xmlpath

xmlStorage = XMLFileSystemStorage('xml/upload')


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
    file = models.FileField(storage=xmlStorage)  # upload_to parametresi olmamalı burada, yoksa upload edemiyor.
    remote_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

    def get_file_path(self):
        # img = self.image
        if self.file and hasattr(self.file, 'url'):
            file_url = self.file.url
            print("before :", file_url)
            # remove STATIC_URL from img_url in our case /static/
            file_url = file_url.replace(settings.STATIC_URL, "/", 1)
            print("after :", file_url)
            # # combine with STATIC_ROOT location in our case /static_root (Trailing slash koyma!!!!!!!!)

            file_path = settings.STATIC_ROOT + file_url  # os.path.join does not joins what the fuck!!!!
            print("file_path :", file_path)

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
