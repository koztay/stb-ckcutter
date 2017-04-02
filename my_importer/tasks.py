from __future__ import absolute_import, unicode_literals
from django.conf import settings
from celery.decorators import task

from .models import XMLImportMap, ImporterFile
from utils import image_downloader
from products.models import Product, ProductType, Currency, Category

import json
from . import xml_processor

# TODO: Currency ve Product Type, Barkod vb. field ları için Validation ekle.

# TODO: http://stackoverflow.com/questions/11618390/celery-having-sequential-tasks-rather-than-concurrent
"""
Single worker consuming from a queue with concurrency equals to one ensures that the tasks-delete-this will be processed in
sequential order. In other words you can create a special queue and run only one celery worker with concurrency
equals to one:

celery -A tasks-delete-this worker -Q amazon_queue -c 1
And submit tasks-delete-this to that queue:

tasks-delete-this.add.apply_async(args=[1,2], kwargs={}, queue='amazon_queue')
Or use automatic routing for certain task types.
"""

# Udemy Complete Object Bootcamp" - "Jose PORTILLA"
# TODO: Aşağıdaki fonksiyonda "list comprehension" kullanılabilir mi? - LECTURE 37
# TODO: Aşağıdaki fonksiyonda "lambda expressions" kullanılabilir mi? get_cell_for_field() 'da kesin kullanılır. - L42
# TODO: Aşağıdaki fonksiyonda "map", "reduce", "filter", zip kullanılabilir mi? lambda ile birlikte - L71,72,73,74

# ins = [x for x in instance_list if type(x).__name__=="int"]
# instance = lambda modelstring, instancelist: [x for x in instance_list if type(x).__name__==modelstring][0]
# yukarıdaki iki fonksiyon da çalıştı.


# @task(bind=True, name="Import_XML_File", rate_limit="10/h")
def import_xml_file(self, xml_file_pk=None, import_map_pk=None):
    """
    Bu task tüm import işlemini tek seferde yapacak. O nedenle rate için saate 10 adet yazdım.
    :param self: task 'in kendisi, daha sonra refere etmek için gerekli sanırım
    :param xml_file_pk: hangi xml 'i import edeceksek onu gönderiyoruz.
    :param import_map_pk: xml 'i import ederken hangi mapi kullanacaksak onu gönderiyoruz.
    :return: import edilen ürüne ait ürün adını göndereceğiz.
    """

    # xml_file_pk=34
    # import_map_pk = 33

    # 1- xml 'dosyasını aç rootu get_children() ile de tüm children elementleri al.
    # 2- import_map 'ten map json 'ı oluştur.
    # 3- import edilecek field 'ları bul. XML_Field içerenler, diğerlerini alma.
    # 4- Şimdi sırasıyla loop yaparak ürünleri oluşturmaya başla.
    # 5- ürün oluşturma sırası aşağıdaki gibi olacak:
    xml_file_object = ImporterFile.objects.get(pk=xml_file_pk)
    xml_file_path = xml_file_object.get_file_path()
    root = xml_processor.get_root(xml_file_path)
    all_products = root.getchildren()  # we have all products as a element list

    # return import_map field value as string
    import_map_object = XMLImportMap.objects.get(pk=import_map_pk)
    import_map = import_map_object.map

    # return a dictionary from the above string
    json_map = json.loads(import_map)
    # print("type json_map:", type(json_map))  # bunun tipi dictionary imiş

    # product yaratabilmek için gerekli fieldları listele ve product 'ı yarat.
    product_fields = [x for x in json_map if json_map[x].get("model") == "Product"]

    # create an object list from above field list which is processable for getting XML values
    processable_list = list(map(lambda x: json_map[x], product_fields))
    # print(processable_list)

    # below is a list of dictionary objects / find the fields mapped with XML file
    mapped_product_fields = list(filter(lambda x: "XML_Field" in x, processable_list))

    variation_fields = [x for x in json_map if json_map[x].get("model") == "Variation"]
    processable_variation_list = list(map(lambda x: json_map[x], variation_fields))
    mapped_variation_fields = list(filter(lambda x: "XML_Field" in x, processable_variation_list))
    print(mapped_variation_fields)

    # find all mapped fields
    all_mapped_fields = [x for x in json_map if json_map[x].get("XML_Field")]

    # create an object list from mapped fields
    processable_mapped_list = list(map(lambda x: json_map[x], all_mapped_fields))
    # print(processable_mapped_list)
    """
    [
        {'model': 'Category', 'XML_Field': 'Kategori', 'local_field': 'categories'}, 
        {'model': 'Currency', 'XML_Field': 'ParaBirimi', 'local_field': 'name'}, 
        {'model': 'ProductImage', 'XML_Field': 'Resim', 'local_field': 'image'}, 
        {'model': 'Variation', 'XML_Field': 'Kod', 'local_field': 'istebu_product_no'}, 
        {'model': 'NA', 'XML_Field': 'Stok', 'local_field': 'NA'}, 
        {'model': 'Variation', 'XML_Field': 'Fiyat', 'local_field': 'sale_price'}, 
        {'model': 'Product', 'XML_Field': 'Baslik', 'local_field': 'title'}
    ]
    
    yukarıdaki her bir model için bir fonksiyon yaz.

    """

    def set_category(product_instance, category_instance):
        product_instance.categories.add(category_instance)

    def set_currency(variation_instance, currency_instance):
        variation_instance.buying_currency = currency_instance

    def set_product_type(product_instance, product_type_instance):
        product_instance.product_type = product_type_instance

    # product_image için set func yazmaya gerek yok. çünkü image downloader yapacak o işi
    # variation otomatik yaratılıyor o nedenle onun da fieldlarını set etmeliyim.

    def get_xml_field_for_local(field, model):

        # return a default field name list below which contains given field
        field_name_list = [x for x in json_map if json_map[x].get('local_field') == field]

        # return a dictionary list using above field name list
        processable_object_list = list(map(lambda x: json_map[x], field_name_list))
        # print(processable_object_list)

        # return an object from above list which contains the model
        target_object = [x for x in processable_object_list if x.get('model') == model][0]
        # print(target_object)

        # return XML_Field
        return target_object.get("XML_Field")
    # print(get_xml_field_for_local('name', 'Currency'))
    # print(get_xml_field_for_local('title', 'Product'))

    def create_or_update_product_fields(all_product_elements):
        for product_element in all_product_elements:
            xml_field_for_title = get_xml_field_for_local("title", "Product")
            title = product_element.find(xml_field_for_title).text
            # 1- product instance yarat
            product_instance, created = Product.objects.get_or_create(title=title)
            variation_instance = product_instance.variation_set.all()[0]
            print(variation_instance)
            # 2- map edilmiş listeden XML_Field 'ı bul (TAG)
            for field in mapped_product_fields:
                # 3- bulduğun TAG 'e ait değeri çek
                xml_field = field.get("XML_Field")
                # print("xml_field", xml_field)

                xml_field_value = product_element.find(xml_field).text
                # 4- map edilmiş listeden field 'ı çek (local_field)
                local_field = field.get("local_field")
                # 5- set_attribute ile değerleri set et.
                setattr(product_instance, local_field, xml_field_value)

                # 6- save ile variation vs. yaratılmasını sağla, aslında create ile yaratılmış olması lazım.

                # print("product save edildi.")

            # 7- product 'a ait diğer değerleri gir. kategori, type, currency vb.
            for field in processable_mapped_list:
                if field.get("model") == 'Category':
                    xml_field_name = get_xml_field_for_local("categories", "Category")
                    print(xml_field_name)
                    # get category from name and pass it to func

                elif field.get("model") == 'Currency':
                    xml_field_name = get_xml_field_for_local("name", "Currency")
                    print(xml_field_name)
                    # get currency object and pass it to func

                elif field.get("model") == 'ProductType':
                    xml_field_name = get_xml_field_for_local("name", "Currency")
                    print(xml_field_name)

                elif field.get("model") == 'ProductImage':
                    xml_field_name = get_xml_field_for_local("image", "ProductImage")
                    print(xml_field_name)
                    # burada image downloader task başlat

                elif field.get("model") == 'Variation':

                    for field in mapped_variation_fields:

                        xml_field = field.get("XML_Field")
                        print("xml_field", xml_field)

                        xml_field_value = product_element.find(xml_field).text
                        print (xml_field_value)
                        # 4- map edilmiş listeden field 'ı çek (local_field)
                        local_field = field.get("local_field")
                        print(local_field)
                        # 5- set_attribute ile değerleri set et.
                        if xml_field_value:
                            setattr(variation_instance, local_field, xml_field_value)

            variation_instance.save()
            product_instance.save()


            # 8- otomatik olarak yaratılan variantı çek
            # 9- varianta ait değerleri set et ve save edip döngüden çık.

            if created:
                print("product created")
            else:
                print("product_updated")
        print("task_completed")


    # create_or_update_product_fields(all_products)

    create_or_update_product_fields(all_products)

@task(bind=True, name="Download Image", rate_limit="40/h")
def download_image_for_product(self, image_link=None, product_id=None):
    result = "Hata! %s linkindeki resim indirilemedi:" % image_link
    try:
        result = image_downloader.download_image(image_link, product_id)
    except Exception as e:
        self.retry(countdown=120, exc=e, max_retries=2)

    return result


# This task has been added for testing purposes.
@task(bind=True)
def add(self, x, y):
    try:
        raise Exception()
    except Exception as e:
        self.retry(countdown=2, exc=e, max_retries=2)
        # countdown kaç saniye beklemesini belirtiyor, max_retries ise adından belli kaç kez tekrarlanmasını.
    return x + y


@task(bind=True, name="Process XLS Row", rate_limit="20/m")
def process_xls_row(self, importer_map_pk, row, values):  # Bu fonksiyonun no_task olarak views 'da çalıştığı görüldü.
    # Ancak task olarak çalışıp çalışmadığı test edilemedi.
    """
    Please do not forget to create worker with the following command, in command line:
    celery -A ecommerce2 worker -l info
    """
    # pydevd.settrace('192.168.1.22', port=5678, stdoutToServer=True, stderrToServer=True)
    importer_map = ProductImportMap.objects.get(pk=importer_map_pk)

    def get_cell_for_field(field_name):
        try:
            field_object = importer_map.fields_set.get(product_field=field_name)
            cell_value_index = field_object.get_xml_field()  # Adına get_xml_filed demişiz ama xls, xlsx için de aynısı.

            cell_value = values[int(cell_value_index)]  # field eşleştirmeleri 0,1,2 gibi indeks değeri ile yapıldığı
            # için sorun yok. Şimdilik indeks yerine hücreye ait başlık ile eşleştirme yapmayı çözemedim.
        except:
            cell_value = ""
        return cell_value

    def update_default_fields(product_instance=None):

        variation_instance = product_instance.variation_set.all()[0]  # product save edilince otomatik yaratılıyor.

        # default fileds models içerisinde tanımlı
        for main_field in default_fields:
            cell = get_cell_for_field(main_field)
            print("cell_value :", cell)

            # hücrenin Pruduct modelde mi, Variation modelde mi olduğunu bul
            cell_value_model = default_fields[main_field]["model"]
            print("cell_value_model: ", cell_value_model)

            if cell_value_model is "Product":
                print("attribute: ", default_fields[main_field]["field"])
                print("value: ", cell)
                attribute = default_fields[main_field]["field"]
                print("attribute - bunun boş dönmesi gerek: ", attribute)
                if attribute is 'categories':
                    print("kategori yakaladım")
                    try:
                        category = Category.objects.get(title=cell)
                        print("Kategori: ", category)
                        product_instance.categories.add(category)
                    except:
                      print("kategori bulunamadı.")
                else:
                    setattr(product_instance, attribute, cell)
                # setattr(product_instance, attribute, cell)

            elif cell_value_model is "Variation":
                print("attribute: ", default_fields[main_field]["field"])
                print("value: ", cell)
                setattr(variation_instance, default_fields[main_field]["field"], cell)

            elif cell_value_model is "ProductType":
                # product_type_name = default_fields[main_field]["field"]
                # print("product_type_name :", product_type_name)
                product_type_instance, created = ProductType.objects.get_or_create(name=cell)
                product_instance.product_type = product_type_instance

            elif cell_value_model is "Currency":
                print("attribute: ", default_fields[main_field]["field"])
                print("value: ", cell)
                # Eğer currency veriatabanında yoksa o zaman ürünü ekleme. Dolayısıyla "Para Birimi" önceden eklenmeli.
                try:
                    currency_instance = Currency.objects.get(name=cell)
                    variation_instance.buying_currency = currency_instance
                except:
                    print("Currency bulunamadı, %s eklenmedi!" % product.title)
                    pass

                print("variation_instance.buying_currency", variation_instance.buying_currency)

            else:
                print("Hata! Böyle bir model dönmemeli, cell_value_model: ", cell_value_model)

        factor = float(settings.IMPORTER_SALE_PRICE_FACTOR)
        product_instance.price = variation_instance.sale_price*factor

        # ürünlerin fiyatı boş geliyor o nedenle factor kadar yükseltiyoruz...
        product_instance.save()
        variation_instance.save()

    title = get_cell_for_field("Ürün Adı")
    # product_type = ProductType.objects.get(name=importer_map.type)
    product, product_created = Product.objects.get_or_create(title=title)

    update_default_fields(product_instance=product)
    # update_default_fields(product)  # her halükarda yaratılacak o yüzden önemsiz...
    img_url = get_cell_for_field("Image")

    print("IMG URL => :", img_url)
    print('product.id neden görülmüyor baba?', product.id)
    print('product.pk neden görülmüyor baba?', product.pk)
    if product.productimage_set.all().count() == 0:  # image varsa boşu boşuna task ekleme.
        print("Resim daha önce eklenmemiş. Download task çalıştırılacak. Yeni fonksiyon bu.")
        download_image_for_product.delay(img_url, product.id)

    return "%s update edildi." % product.title



