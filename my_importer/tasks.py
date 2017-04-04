from __future__ import absolute_import, unicode_literals
from django.conf import settings
from celery.decorators import task

from .models import XMLImportMap, ImporterFile
from utils import image_downloader
from products.models import Product, ProductType, Currency, Category, Variation

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


"""
Tüm sorgularda aşağıdaki Keyler ile başla, yani örneğin Mağaza_Kodu için XML_Field bulmak için :
json_map.get("Mağaza_Kodu").get("XML_Field)

ya da model için :
json_map.get("Mağaza_Kodu").get("model)

ya da local field için 

"Magaza_Kodu"
"Kategori": 
"Alt_Kategori"
"Urun_Tipi"
"Urun_Adi"
"KDV" 
"Para_Birimi"
"Alis_Fiyati"
"Satis_Fiyati"
"Barkod"
"Kargo"
"Urun_Resmi"
"""



# Udemy Complete Object Bootcamp" - "Jose PORTILLA"
# TODO: Aşağıdaki fonksiyonda "list comprehension" kullanılabilir mi? - LECTURE 37
# TODO: Aşağıdaki fonksiyonda "lambda expressions" kullanılabilir mi? get_cell_for_field() 'da kesin kullanılır. - L42
# TODO: Aşağıdaki fonksiyonda "map", "reduce", "filter", zip kullanılabilir mi? lambda ile birlikte - L71,72,73,74

# ins = [x for x in instance_list if type(x).__name__=="int"]
# instance = lambda modelstring, instancelist: [x for x in instance_list if type(x).__name__==modelstring][0]
# yukarıdaki iki fonksiyon da çalıştı.


# @task(bind=True, name="Import_XML_File", rate_limit="10/h")
def import_xml_file(self, xml_file_pk=None, import_map_pk=None, default_category=None):
    """
    Bu task tüm import işlemini tek seferde yapacak. O nedenle rate için saate 10 adet yazdım.
    :param self: task 'in kendisi, daha sonra refere etmek için gerekli sanırım
    :param xml_file_pk: hangi xml 'i import edeceksek onu gönderiyoruz.
    :param import_map_pk: xml 'i import ederken hangi mapi kullanacaksak onu gönderiyoruz.
    :return: import edilen ürüne ait ürün adını göndereceğiz.
    """

    # xml_file_pk = 35
    # import_map_pk = 34

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
    print(json_map)
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
    # print(mapped_variation_fields)

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

    def get_map_field(field, subfield):
        return json_map.get(field).get(subfield)

    def create_or_update_product_fields(all_product_elements):
        for product_element in all_product_elements:
            xml_field_for_title = get_map_field("Urun_Adi", "XML_Field")
            title = product_element.find(xml_field_for_title).text
            # 1- product instance yarat
            created = False
            try:
                product_instance = Product.objects.get(title=title)
            except Product.DoesNotExist:
                product_instance = Product(title=title)
                created = True
                # at this stage I don't want to save the product in db.
                # so, I don't use Product.objects.create() method
            # variation_instance = product_instance.variation_set.all()[0]  # there is no variation instance
            # print(variation_instance)
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

            # check if mandatory fields have been available.
            save_product = True
            mandatory_field = None

            product_dictionary = xml_processor.get_all_sub_elements_as_dict(product_element)
            kategori = get_map_field("Kategori", "XML_Field")
            # print(kategori)
            if not product_dictionary[0].get(kategori):
                save_product = False
                mandatory_field = "Kategori"

            # yukarıda false yapılmamışsa
            if save_product:
                product_instance.save()

                # artık aşağıdaki maddeleri girebiliriz. Çünkü mandatory field lar tamam.
                # 7- product 'a ait diğer değerleri gir. kategori, type, currency vb.
                for field in processable_mapped_list:
                    if field.get("model") == 'Category':
                        try:
                            category_instance = Category.objects.get(title=product_dictionary[0].get(kategori))
                            set_category(product_instance, category_instance)
                            print("Kategori Bulundu.")
                        except:
                            print("Kategori Bulunamadı...")



                    elif field.get("model") == 'Currency':
                        xml_field_name = get_xml_field_for_local("name", "Currency")
                        print(xml_field_name)
                        # get currency object and pass it to func

                    elif field.get("model") == 'ProductType':
                        xml_field_name = get_xml_field_for_local("name", "ProductType")
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

            if save_product:
                variation_instance.save()
                product_instance.save()
            else:
                print("There is a missing mandatory field: %s.  It prevents saving product.", mandatory_field)

            # 8- otomatik olarak yaratılan variantı çek
            # 9- varianta ait değerleri set et ve save edip döngüden çık.

            if created:
                print("product created")
            else:
                print("product_updated")

        print("task_completed")


    # create_or_update_product_fields(all_products)

    create_or_update_product_fields(all_products)


def step01_prepare_xml_for_processing(xml_file_pk):
    """
      Bu task tüm import işlemini tek seferde yapacak. O nedenle rate için saate 10 adet yazdım.
      :param self: task 'in kendisi, daha sonra refere etmek için gerekli sanırım
      :param xml_file_pk: hangi xml 'i import edeceksek onu gönderiyoruz.
      :return: import edilen ürüne ait ürün adını göndereceğiz.
      """

    # xml_file_pk = 35
    # import_map_pk = 34
    xml_file_object = ImporterFile.objects.get(pk=xml_file_pk)
    xml_file_path = xml_file_object.get_file_path()
    root = xml_processor.get_root(xml_file_path)
    products_dictionary_array = xml_processor.get_all_sub_elements_as_dict(root)
    return products_dictionary_array


""" 
    "Barkod": {"model": "Variation", "local_field": "product_barkod"},
    "Alis_Fiyati": {"model": "Variation", "local_field": "buying_price"},
    "Satis_Fiyati": {"model": "Variation", "local_field": "sale_price"},  
    "Magaza_Kodu": {"model": "Variation", "local_field": "istebu_product_no"},
    "Para_Birimi": {"model": "Currency", "local_field": "name"},  # variation.buying_currency olarak ekle!!!
    "Kategori": {"model": "Category", "local_field": "categories"},  # product.categories olarak eklenecek !!!!
    "Alt_Kategori": {"model": "Category", "local_field": "categories"}, # product.categories olarak eklenecek !!!
    "Urun_Tipi": {"model": "ProductType", "local_field": "name"},  # product.product_type olarak ekle !!!
    "Urun_Adi": {"model": "Product", "local_field": "title"},
    "KDV": {"model": "Product", "local_field": "kdv"},
    "Urun_Resmi": {"model": "ProductImage", "local_field": "image"},

"""


def step02_prepare_import_map(import_map_pk):
    # return import_map field value as string
    import_map_object = XMLImportMap.objects.get(pk=import_map_pk)
    import_map = import_map_object.map

    # return a dictionary from the above string
    return json.loads(import_map)


def process_dict(row_dictionary):
    # print(row_dictionary)
    pass

def step03_process_products_dict_array(product_dict_array, json_map):
    # variation_fields = ["Barkod", "Alis_Fiyati", "Satis_Fiyati", "Magaza_Kodu"]
    # currency_fields = ["Para_Birimi"]
    # kategori_fields = ["Kategori", "Alt_Kategori"]
    # product_type_fields = ["Urun_Tipi"]
    # product_fields = ["Urun_Adi", "KDV"]
    # product_picture_fields = ["Urun_Resmi"]

    for number, product_dict in enumerate(product_dict_array):
        row_dictionary = dict()
        # print(product_dict)

        # ileride field 'a ait is_mandatory ve default_value değerlerini de json_map içerisine entegre etme
        # imkanı olursa 4x4  'lük bir xml importer 'ımız olur.

        def calculate_default_alis_fiyati():
            # ("%.2f" % a)
            return round(float(row_dictionary.get('Satis_Fiyati').get('sale_price'))*0.95, 2)

        def create_magazakodu(prefix, suffix):  # bunu bir kerelik çalıştır. Bu bizim için mağaza kodu oluşturuyor.
            print("Çalıştım")

            kod_query_set = Variation.objects.filter(istebu_product_no__icontains=prefix)
            print(kod_query_set)
            if kod_query_set:
                kod_array = [int(kod.istebu_product_no[len(prefix):]) for kod in kod_query_set]
                last_number = max(kod_array)
                return prefix+(last_number+1)
            else:
                return prefix + str(int(suffix) + number)

        def process_field(field, is_mandatory, default_value=None):

            xml_field = json_map.get(field).get("XML_Field")
            xml_value = product_dict.get(xml_field)
            local_field = json_map.get(field).get("local_field")

            if xml_value is not None:  # XML eşleştirmesi yapılmış.
                xml_value = xml_value.strip()  # Eşleştirilen field XML 'den okunmuş.
                if xml_value:  # Eşleştirilen field XML 'den başarıyla okunmuş. (2 rakamlı TL vs. ise ?)
                    # strip edince '\n' karakterleri falan hepsi gidiyor. O nedenle >= vs. gibi bir checke gerek yok.
                    value_dict = {local_field: xml_value}
                    row_dictionary[field] = value_dict
                    # print("xml value olarak bulup yazdım.", local_field, xml_value)
                    return True
                else:  # XML 'den saçma bir değer okunmuş. Dolayısıyla row 'a yazılamaz.
                    if default_value:  # zorunlu ya da değil default değer girilmiş mi bak
                        value_dict = {local_field: default_value}
                        row_dictionary[field] = value_dict  # varsa default değeri ekle
                        # print("default tan bulup yazdım.", local_field, default_value)
                        return True
                    else:  # default değer yok.
                        return False  # zorunlu ve default değer yoksa False döndür.

            elif is_mandatory:  # (XML 'de eşleştirilmemiş ve zorunlu. Default değerleri yine girmeye çalış.)
                if default_value:  # zorunlu ise default değer girilmiş mi bak
                    value_dict = {local_field: default_value}
                    row_dictionary[field] = value_dict  # default değeri ekle
                    return True
                else:  # Giremediyse yani hem zorunlu hem de default değer yok. Örneğin satış fiyatı...
                    return False  # False döndür.

            else:  # Hem eşleşmemiş hem de zorunlu da değilse
                return False

        if not process_field("Urun_Adi", True, default_value=None):  # default değer girilemez.
            print("Urun adi does not exist, will break")
            continue

        if not process_field("Satis_Fiyati", True, default_value=None):  # default değer girilemez.
            print("No Satis_Fiyati, will break")
            continue

        if not process_field("Kategori", True, default_value="Projeksiyon Cihazları"):  # Mandatory field break necessary
            # set default as TL
            print("No Kategori, will break")
            continue

        if not process_field("Barkod", False, default_value=None):  # Not mandatory field Break is not necessary
            # do nothing
            pass

        alis_fiyati = calculate_default_alis_fiyati()  # bunu fonksiyon olarak göndermeyi başaramadım bir türlü
        if not process_field("Alis_Fiyati", True, default_value=alis_fiyati):
            """
            default değerin işleme alınabilmesi için mandatory = True olmalı.
            """
            # Not mandatory field Break is not necessary
            # set field according to the Satis_Fiyati e.g. 0.95
            print("Amına koyayım neden set etmiyor bu amcık ağızlı?")
            buying_price = row_dictionary.get('Satis_Fiyati').get('sale_price')
            continue

        print("Mağaza Kodu:", create_magazakodu("PRJ", "1000"))  # Bunu ürünü save ederken çalıştırmak lazım...
        if not process_field("Magaza_Kodu", False, default_value=None):  # Bu bizim vereceğimiz kod otomatik oluşmalı bence
            # create mağaza kodu
            pass

        if not process_field("Para_Birimi", False, default_value=None):
            # set default as TL
            pass

        if not process_field("Alt_Kategori", False, default_value=None):
            # set it if it exists
            pass

        if not process_field("Urun_Tipi", False, default_value=None):
            # set it if it exists
            pass

        if not process_field("Urun_Resmi", False, default_value=None):
            # set it if it exists (it will create
            pass

        # buraya kadar break olmadan geldiyse process dict fonksiyonunu çalıştır
        process_dict(row_dictionary)


# ileride XLSX, XLS import içinde kullanılabilmesi için adını run_all_xml_steps şeklinde değiştirmek gerekebilir.
def run_all_steps():
    products_dict_array = step01_prepare_xml_for_processing(35)
    json_map = step02_prepare_import_map(34)
    step03_process_products_dict_array(products_dict_array, json_map)


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



