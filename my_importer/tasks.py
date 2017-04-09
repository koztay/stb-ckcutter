from __future__ import absolute_import, unicode_literals

import shutil

import urllib3
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


# bu fonksiyon ürün create ediliyorsa ve dictionary ile kod gelmemişse çalışmalı ancak ürün update edilirken
# çalışmamalı. Fakat reference number' nasıl göndereceğiz döngü yok birşey yok... Şuna bakabilirsin db'den verilen
# prefixi içeren bir magaza kodu var mı? Eğer varsa suffix 'i hiç dikkate almazsın. Yoksa prefix+suffix için başlangıç
# noktası kabul edersin ve bu durumda artık db 'de prefix içeren magaza kodu var artık demektir. Sonrasında bunu alır
# her seferinde +1 yaparsın... Aşağıda bunu yapmışım zaten...
def create_magazakodu(prefix, suffix, variation_id):
    kod_query_set = Variation.objects.filter(istebu_product_no__icontains=prefix)
    # print(kod_query_set)
    variation_instance = Variation.objects.get(pk=variation_id)
    if not variation_instance.istebu_product_no:  # Eğer kod varsa girme, yoksa gir...
        if kod_query_set:
            kod_array = [int(kod.istebu_product_no[len(prefix):]) for kod in kod_query_set]
            last_number = max(kod_array)
            return prefix + str((last_number + 1))
        else:
            return prefix + str(suffix)
    else:
        return variation_instance.istebu_product_no


# buraya tüm kontroller yapılıp gelmiş durumda dictioanry olarak. O nedenle get_or_create kullanabilirim.
@task(bind=True, name="Process Dict Row", rate_limit="20/m")
def process_dict(self, row_dictionary, create_allowed):
    # variation_fields = ["Barkod", "Alis_Fiyati", "Satis_Fiyati", "Magaza_Kodu"]
    # currency_fields = ["Para_Birimi"]
    # kategori_fields = ["Kategori", "Alt_Kategori"]
    # product_type_fields = ["Urun_Tipi"]
    # product_fields = ["Urun_Adi", "KDV"]
    # product_picture_fields = ["Urun_Resmi"]
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

    # print(row_dictionary)
    product_title = row_dictionary.get("Urun_Adi").get("title")

    created = False

    if create_allowed is True:
        product_instance, created = Product.objects.get_or_create(title=product_title)
        # product_instance.kdv 'yi set etmeye gerek yok, çünkü default değeri var modelde.
    else:
        try:
            if Product.objects.all():
                # active True olabilmesi için eksiksiz olarak fieldların tamamlanmış olması lazım...
                product_instance = Product.objects.all().get(title=product_title, active=False)
            else:
                print("I cannot query any products. Please add one manually or run the function with create=True")
                return
        except LookupError:
            return  # exit processing row_dictionary

    if row_dictionary.get("KDV"):
        product_kdv = row_dictionary.get("KDV").get("kdv")
        product_instance.kdv = product_kdv

    # Product filedları bitti sıra variationlarda...
    variation_instance = product_instance.variation_set.all()[0]  # birden fazla variation varsa ne bok yiycen?

    if row_dictionary.get("Barkod"):
        variation_barkod = row_dictionary.get("Barkod").get("product_barkod")
        variation_instance.product_barkod = variation_barkod

    if row_dictionary.get("Stok"):
        variation_stok = row_dictionary.get("Stok").get("inventory")
        variation_instance.inventory = variation_stok

    # if row_dictionary.get("Magaza_Kodu"):
    #     variation_magaza_kodu = row_dictionary.get("Magaza_Kodu").get("istebu_product_no")
    #     variation_instance.istebu_product_no = variation_magaza_kodu
    # elif variation_instance.istebu_product_no is None:
    #     variation_instance.istebu_product_no = create_magazakodu("PRJ", "1000")  # her xml için farklı olmalıç

    variation_instance.istebu_product_no = create_magazakodu("PRJ", "1000", variation_id=variation_instance.id)


    # zorunlu alan:
    variation_instance.buying_price = row_dictionary.get("Alis_Fiyati").get("buying_price")
    # zorunlu alan:
    variation_instance.sale_price = row_dictionary.get("Satis_Fiyati").get("sale_price")
    product_instance.price = row_dictionary.get("Satis_Fiyati").get("sale_price")  # product 'a da eklemeliyiz.

    variation_buying_currency = row_dictionary.get("Para_Birimi").get("name")
    # DIKKAT!!! : önceden sistemde currency 'lerin tanımlı olması gerek... Değilse fonksiyonu sonlandır.
    if variation_buying_currency:
        # NAME_CHOICES = (
        #     ("TL", "TURK LIRASI"),
        #     ("USD", "AMERIKAN DOLARI"),
        #     ("EUR", "EURO"),
        # )
        # DATABASE 'deki değerler "TL", "USD, "EUR" olmalı. O nedenle sorgularken de öyle sorgulamalı.


        currency_symbols = {
            "TURK LIRASI": ["TL", "₺"],
            "AMERIKAN DOLARI": ["USD", "$"],
            "EURO": ["EUR", "EURO", "€"],
        }

        try:
            currency_instance = Currency.objects.get(name=variation_buying_currency)  # TL, ₺ gibi bir değer dönecek
            variation_instance.buying_currency = currency_instance
        except LookupError:
            pass  # buying currency set edilmemiş şekilde kaydet...

    product_category = row_dictionary.get("Kategori").get("categories")
    # DIKKAT!!! : önceden sistemde kategorinin yaratılmış olması lazım... Değilse fonksiyonu sonlandır.
    if product_category:
        try:
            category_instance = Category.objects.get(title=product_category)
            product_instance.categories.add(category_instance)
        except LookupError:
            pass  # product category set edilmemiş şekilde kaydet...

    if row_dictionary.get("Alt_Kategori"):
        product_sub_category = row_dictionary.get("Alt_Kategori").get("categories")
        if product_sub_category:  # bazı filedlarda var bazılarında yok olabilir.
            try:
                category_instance = Category.objects.get(title=product_sub_category)
                product_instance.categories.add(category_instance)
            except LookupError:
                pass  # product category set edilmemiş şekilde kaydet...

    if row_dictionary.get("Urun_Tipi"):
        product_type = row_dictionary.get("Urun_Tipi").get("name")
        # DIKKAT!!! : önceden sistemde kategorinin yaratılmış olması lazım... Değilse fonksiyonu sonlandır.
        if product_type:
            try:
                product_type_instance = ProductType.objects.get(name=product_type)
            except LookupError:
                pass  # product type set edilmemiş şekilde kaydet...

    if row_dictionary.get("Aciklama"):
        description = row_dictionary.get("Aciklama").get("description")
        if description:
            product_instance.description = description
            print("açıklama alanını güncelledim.")
        else:
            print("açıklama alanını güncelleyemedim.")

    product_instance.active = True
    product_instance.save()
    variation_instance.save()

    if row_dictionary.get("Urun_Resmi"):
        product_picture = row_dictionary.get("Urun_Resmi").get("image")
        if product_picture:
            if product_instance.productimage_set.all().count() == 0:  # image varsa boşu boşuna task ekleme.
                print("Resim daha önce eklenmemiş. Download task çalıştırılacak. Yeni fonksiyon bu.")
                download_image_for_product.delay(product_picture, product_instance.id)

    if created:
        return "%s sisteme eklendi." % product_instance.title
    else:
        return "%s update edildi." % product_instance.title


def step03_process_products_dict_array(product_dict_array, json_map, create_allowed):
    # TODO : Açıklama field 'ını da al projeksiyon.xml 'den
    # TODO : Filigransız resimleri al.

    # variation_fields = ["Barkod", "Alis_Fiyati", "Satis_Fiyati", "Magaza_Kodu"]
    # currency_fields = ["Para_Birimi"]
    # kategori_fields = ["Kategori", "Alt_Kategori"]
    # product_type_fields = ["Urun_Tipi"]
    # product_fields = ["Urun_Adi", "KDV"]
    # product_picture_fields = ["Urun_Resmi"]
    print("processing product dictionary array")

    for number, product_dict in enumerate(product_dict_array):  # madem number göndermeyeceğiz o vakit neden
        row_dictionary = dict()
        # print(product_dict)
        # ileride field 'a ait is_mandatory ve default_value değerlerini de json_map içerisine entegre etme
        # imkanı olursa 4x4  'lük bir xml importer 'ımız olur.

        def calculate_default_alis_fiyati():
            # ("%.2f" % a)
            return round(float(row_dictionary.get('Satis_Fiyati').get('sale_price'))*0.95, 2)

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
                    print("xml value olarak bulup yazdım.", local_field, xml_value)
                    return True
                else:  # XML 'den saçma bir değer okunmuş. Dolayısıyla row 'a yazılamaz.
                    if default_value:  # zorunlu ya da değil default değer girilmiş mi bak
                        value_dict = {local_field: default_value}
                        row_dictionary[field] = value_dict  # varsa default değeri ekle
                        print("default tan bulup yazdım.", local_field, default_value)
                        return True
                    else:  # default değer yok.
                        print("False döndürüyorum - 1")
                        return False  # zorunlu ve default değer yoksa False döndür.

            elif is_mandatory:  # (XML 'de eşleştirilmemiş ve zorunlu. Default değerleri yine girmeye çalış.)
                if default_value:  # zorunlu ise default değer girilmiş mi bak
                    value_dict = {local_field: default_value}
                    row_dictionary[field] = value_dict  # default değeri ekle
                    return True
                else:  # Giremediyse yani hem zorunlu hem de default değer yok. Örneğin satış fiyatı...
                    print("False döndürüyorum - 2")
                    return False  # False döndür.

            else:  # Hem eşleşmemiş hem de zorunlu da değilse
                print("False döndürüyorum - 3")
                return False

        if not process_field("Urun_Adi", True, default_value=None):  # default değer girilemez.
            print("Urun adi does not exist, will break")
            continue
        else:
            urun_adi = row_dictionary.get("Urun_Adi").get('title')  # yukarıda continue olduğu için burada and gereksiz.
            if "Perde" in urun_adi:
                continue
            elif "DA-LITE" in urun_adi:
                continue
            elif "PROCOLOR" in urun_adi:
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

        #  print("Mağaza Kodu:", create_magazakodu("PRJ", "1000", number))  # Bunu ürünü save ederken çalıştırmak lazım
        if not process_field("Magaza_Kodu", False, default_value=None):  # Bu bizim vereceğimiz kod otomatik oluşmalı
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
        else:
            # post porcess the field here change the image url // acaba bunu decorator olarak yazamaz mıyım?
            img_url = row_dictionary.get("Urun_Resmi").get('image')
            if img_url and "filigran" in img_url:  # yukarıda pass olduğu için burada img_url olduğundan emin olmalıyız.
                new_url = img_url.replace("filigran", "urun")
                row_dictionary["Urun_Resmi"]["image"] = new_url  # update etmelisin...

        if not process_field("Aciklama", False, default_value=None):
            pass

        if not process_field("Stok", False, default_value=None):
            pass
        # buraya kadar break olmadan geldiyse process dict fonksiyonunu çalıştır
        print("send process request for row dictionary")
        process_dict.delay(row_dictionary, create_allowed)

    print("finsihed processing products")

# ileride XLSX, XLS import içinde kullanılabilmesi için adını run_all_xml_steps şeklinde değiştirmek gerekebilir.
# TODO : Bunun için en iyisi bir class yazmak. Ondan sonra da o class 'ın fonksiyonlarını yazarsın. Mesela :
# TODO : drop_row_if_title_contains(), replace_text_in_img_url() vb. gibi.


# bunu task olarak tanımlayıp otomatiğe bağlayabilirim.
def download_xml(xml_file_pk):

    http = urllib3.PoolManager()
    xml_file_object = ImporterFile.objects.get(pk=xml_file_pk)
    url = xml_file_object.remote_url

    file_path = xml_file_object.get_file_path()

    with http.request('GET', url, preload_content=False) as resp, open(file_path, 'wb') as out_file:
        if resp.status is 200:
            shutil.copyfileobj(resp, out_file)
        else:
            raise ValueError('A very specific bad thing happened. Response code was not 200')

    run_all_steps(xml_file_pk)  # eğer burada da hata çıkmazsa update edilmiş ve True döndürülmüş demektir.
    return True


def run_all_steps(xml_file_pk, create_allowed=False):
    products_dict_array = step01_prepare_xml_for_processing(xml_file_pk)[:50]  # 50 adet için test ediyoruz.
    # print(products_dict_array)
    xml_file_object = ImporterFile.objects.get(pk=xml_file_pk)
    map_object = xml_file_object.import_map

    json_map = step02_prepare_import_map(map_object.pk)
    print("printing jason map", json_map)
    step03_process_products_dict_array(products_dict_array, json_map, create_allowed)


@task(bind=True, name="Download Image", rate_limit="240/h") # please change me from 240 to 40 on production
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



