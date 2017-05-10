import urllib3
import shutil

from celery.decorators import task

from importer.models import ImporterFile

from .generic_importer import run_all_steps


@task(name="Remote XML Update")
def download_xml(**kwargs):
    xml_file_pk = kwargs.get("xml_file_pk")
    import_map_pk = kwargs.get("import_map_pk")
    number_of_items = kwargs.get("number_of_items")
    download_images = kwargs.get("download_images")
    allow_item_creation = kwargs.get("allow_item_creation")

    http = urllib3.PoolManager()
    xml_file_object = ImporterFile.objects.get(pk=xml_file_pk)
    url = xml_file_object.remote_url

    file_path = xml_file_object.get_file_path()

    with http.request('GET', url, preload_content=False) as resp, open(file_path, 'wb') as out_file:
        if resp.status is 200:
            shutil.copyfileobj(resp, out_file)
        else:
            raise ValueError('A very specific bad thing happened. Response code was not 200')

    run_all_steps(xml_file_pk=xml_file_pk, import_map_pk=import_map_pk,
                  number_of_items=number_of_items, download_images=download_images,
                  allow_item_creation=allow_item_creation)
    return True
