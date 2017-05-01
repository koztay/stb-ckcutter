from __future__ import absolute_import, unicode_literals
from django.conf import settings
from celery.decorators import task

from .models import ProductImportMap
from utils import image_downloader
from products.models import Product, ProductType, Currency, Category, AttributeType, AttributeValue


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


@task(bind=True, name="Process XLS Row", rate_limit="20/m")  # bunu importer_map_pk istemeyecek hale getirince birleştir.
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
        default_fields = settings.DEFAULT_FIELDS
        # default fileds models içerisinde tanımlı
        for main_field in default_fields:
            cell = get_cell_for_field(main_field)
            print("cell_value :", cell)

            # hücrenin Pruduct modelde mi, Variation modelde mi olduğunu bul
            cell_value_model = default_fields[main_field]["model"]
            print("cell_value_model: ", cell_value_model)

            if cell_value_model is "Product":
                print("attribute: ", default_fields[main_field]["local_field"])
                print("value: ", cell)
                attribute = default_fields[main_field]["local_field"]
                print("attribute - bunun boş dönmesi gerek: ", attribute)
                if attribute is 'categories':  # Burası hiç çalışmıyor, hiç True dönmüyor...
                    print("kategori yakaladım")
                    try:
                        category = Category.objects.get(title=cell)
                        print("Kategori: ", category)
                        product_instance.categories.add(category)
                    except:
                      print("kategori bulunamadı.")
                elif attribute is 'title':
                    print("pas geçilecek.")
                    pass  # Title ise boş geç çünkü ben set ettim aşağıda...
                else:
                    setattr(product_instance, attribute, cell)
                # setattr(product_instance, attribute, cell)

            elif cell_value_model is "Variation":
                print("attribute: ", default_fields[main_field]["local_field"])
                print("value: ", cell)
                setattr(variation_instance, default_fields[main_field]["local_field"], cell)

            elif cell_value_model is "ProductType":
                # product_type_name = default_fields[main_field]["local_field"]
                # print("product_type_name :", product_type_name)
                product_type_instance, created = ProductType.objects.get_or_create(name=cell)
                product_instance.product_type = product_type_instance

            elif cell_value_model is "AttributeValue":
                attributetype_instance = AttributeType.objects.get(type="Marka")
                AttributeValue.objects.get_or_create(attribute_type=attributetype_instance,
                                                     product=product_instance,
                                                     value=cell)

            elif cell_value_model is "Currency":
                print("attribute: ", default_fields[main_field]["local_field"])
                print("value: ", cell)
                # Eğer currency veriatabanında yoksa o zaman ürünü ekleme. Dolayısıyla "Para Birimi" önceden eklenmeli.
                try:
                    currency_instance = Currency.objects.get(name=cell)
                    variation_instance.buying_currency = currency_instance
                except:
                    print("Currency bulunamadı, %s eklenmedi!" % product.title)
                    pass

                print("variation_instance.buying_currency", variation_instance.buying_currency)

            elif cell_value_model is "Category":
                try:
                    category = Category.objects.get(title=cell)
                    print("Kategori: ", category)
                    product_instance.categories.add(category)
                except:
                    print("Kategori bulunamadı lütfen ekleyin : ", category)

            else:
                print("Hata! Böyle bir model dönmemeli, cell_value_model: ", cell_value_model)

        factor = float(settings.IMPORTER_SALE_PRICE_FACTOR)
        product_instance.price = variation_instance.sale_price*factor

        # ürünlerin fiyatı boş geliyor o nedenle factor kadar yükseltiyoruz...
        product_instance.save()
        variation_instance.save()

    title = get_cell_for_field("Urun_Adi")
    vendor_urun_kodu = get_cell_for_field("Vendor_Urun_Kodu")  # bunu eşleştirdim.
    print("vendor kod :", vendor_urun_kodu)
    istebu_magaza_kodu = get_cell_for_field("Magaza_Kodu")
    print("magaza kod :", istebu_magaza_kodu)
    # magaza kodu alanı varsa import edilen dokümanda o zaman magaza kodunu kullan
    if vendor_urun_kodu:
        print("vendor kod var burada bulması lazım ürünü...")
        product, product_created = Product.objects.get_or_create(vendor_product_no=vendor_urun_kodu)
        if product_created:
            print("buraya sadece product yaratılmışsa düşmesi lazım...")
            product.title = title
    else:
        print("vendor kod yok eşleşecek alan sadece title")
        # product_type = ProductType.objects.get(name=importer_map.type)
        product, product_created = Product.objects.get_or_create(title=title)

    # Artık product yaratıldı. O nedenle magaza kodu için aşağıdaki kontrolü böyle yapabiliriz.
    if istebu_magaza_kodu:
        product.istebu_product_no = istebu_magaza_kodu
    else:
        product.istebu_product_no = vendor_urun_kodu  # buraya vendor urun kodunu yazmak ne derece doğru?

    update_default_fields(product_instance=product)
    # update_default_fields(product)  # her halükarda yaratılacak o yüzden önemsiz...
    img_url = get_cell_for_field("Urun_Resmi")

    # print("IMG URL => :", img_url)
    # print('product.id neden görülmüyor baba?', product.id)
    # print('product.pk neden görülmüyor baba?', product.pk)
    if product.productimage_set.all().count() == 0:  # image varsa boşu boşuna task ekleme.
        print("Resim daha önce eklenmemiş. Download task çalıştırılacak. Yeni fonksiyon bu.")
        # download_image_for_product.delay(img_url, product.id)
        download_image_for_product.apply_async(args=[img_url, product.id], kwargs={}, queue='images')

    if product_created:
        return "%s veritabanına eklendi." % product.title
    else:
        return "%s update edildi." % product.title


def process_xml_row(self, row):

    def get_value_for_field(field_name):
        db_field = settings.DEFAULT_FIELDS.get(field_name).get('local_field')
        if field_name is 'Urun_Resmi':
            return [d.get('value') for d in row if d.get('field') is db_field]
        elif field_name is "Magaza_Kodu":
            print("Magaza Kodu için birşeyler yap")
        else:
            value = [d.get('value') for d in row if d.get('field') is db_field]
            if len(value) > 0:
                if isinstance([d.get('value') for d in row if d.get('field') is db_field][0], list):
                    return [d.get('value') for d in row if d.get('field') is db_field][0][0]
                else:
                    return [d.get('value') for d in row if d.get('field') is db_field][0]
            else:
                return None

    def update_default_fields(product_instance=None):

        variation_instance = product_instance.variation_set.all()[0]  # product save edilince otomatik yaratılıyor.
        default_fields = settings.DEFAULT_FIELDS
        # default fileds models içerisinde tanımlı
        for main_field in default_fields:
            cell = get_value_for_field(main_field)
            print("cell_value :", cell)

            # hücrenin Pruduct modelde mi, Variation modelde mi olduğunu bul
            cell_value_model = default_fields[main_field]["model"]
            print("cell_value_model: ", cell_value_model)

            if cell_value_model is "Product":
                print("attribute: ", default_fields[main_field]["local_field"])
                print("value: ", cell)
                attribute = default_fields[main_field]["local_field"]
                if attribute is 'categories':  # Burası hiç çalışmıyor, hiç True dönmüyor...
                    print("kategori yakaladım")
                    try:
                        category = Category.objects.get(title=cell)
                        print("Kategori: ", category)
                        product_instance.categories.add(category)
                    except:
                      print("kategori bulunamadı.")
                elif attribute is 'title':
                    print("pas geçilecek.")
                    pass  # Title ise boş geç çünkü ben set ettim aşağıda...
                else:
                    setattr(product_instance, attribute, cell)
                # setattr(product_instance, attribute, cell)

            elif cell_value_model is "Variation":
                print("attribute: ", default_fields[main_field]["local_field"])
                print("value: ", cell)
                setattr(variation_instance, default_fields[main_field]["local_field"], cell)

            elif cell_value_model is "ProductType":
                # product_type_name = default_fields[main_field]["local_field"]
                # print("product_type_name :", product_type_name)
                product_type_instance, created = ProductType.objects.get_or_create(name=cell)
                product_instance.product_type = product_type_instance

            elif cell_value_model is "AttributeValue":
                attributetype_instance = AttributeType.objects.get(type="Marka")
                AttributeValue.objects.get_or_create(attribute_type=attributetype_instance,
                                                     product=product_instance,
                                                     value=cell)

            elif cell_value_model is "Currency":
                print("attribute: ", default_fields[main_field]["local_field"])
                print("value: ", cell)
                # Eğer currency veriatabanında yoksa o zaman ürünü ekleme. Dolayısıyla "Para Birimi" önceden eklenmeli.
                try:
                    currency_instance = Currency.objects.get(name=cell)
                    variation_instance.buying_currency = currency_instance
                except:
                    print("Currency bulunamadı, %s eklenmedi!" % product.title)
                    pass

                print("variation_instance.buying_currency", variation_instance.buying_currency)

            elif cell_value_model is "Category":
                try:
                    category = Category.objects.get(title=cell)
                    print("Kategori: ", category)
                    product_instance.categories.add(category)
                except:
                    print("Kategori bulunamadı lütfen ekleyin : ", cell)

            else:
                print("Hata! Böyle bir model dönmemeli, cell_value_model: ", cell_value_model)

        factor = float(settings.IMPORTER_SALE_PRICE_FACTOR)
        product_instance.price = float(variation_instance.sale_price)*factor

        # ürünlerin fiyatı boş geliyor o nedenle factor kadar yükseltiyoruz...
        product_instance.save()
        variation_instance.save()

    title = get_value_for_field("Urun_Adi")  # it is a list contains another list
    print("title list mi kine acabağı?:", title)
    vendor_urun_kodu = get_value_for_field("Vendor_Urun_Kodu")  # bunu eşleştirdim.
    print("vendor kod :", get_value_for_field)
    istebu_magaza_kodu = get_value_for_field("Magaza_Kodu")
    print("magaza kod :", istebu_magaza_kodu)
    # magaza kodu alanı varsa import edilen dokümanda o zaman magaza kodunu kullan
    if vendor_urun_kodu:
        print("vendor kod var burada bulması lazım ürünü...")
        product, product_created = Product.objects.get_or_create(vendor_product_no=vendor_urun_kodu)
        if product_created:
            print("buraya sadece product yaratılmışsa düşmesi lazım...")
            product.title = title
    else:
        print("vendor kod yok eşleşecek alan sadece title")
        # product_type = ProductType.objects.get(name=importer_map.type)
        product, product_created = Product.objects.get_or_create(title=title)

    # Artık product yaratıldı. O nedenle magaza kodu için aşağıdaki kontrolü böyle yapabiliriz.
    if istebu_magaza_kodu:
        product.istebu_product_no = istebu_magaza_kodu
    else:
        product.istebu_product_no = vendor_urun_kodu  # buraya vendor urun kodunu yazmak ne derece doğru?

    update_default_fields(product_instance=product)
    # update_default_fields(product)  # her halükarda yaratılacak o yüzden önemsiz...
    img_url_list = get_value_for_field("Urun_Resmi")  # TODO: Şimdilik sadece tek resim alabiliyoruz. İleride düzelt.

    # print("IMG URL => :", img_url)
    # print('product.id neden görülmüyor baba?', product.id)
    # print('product.pk neden görülmüyor baba?', product.pk)
    if product.productimage_set.all().count() == 0:  # image varsa boşu boşuna task ekleme.
        print("Resim daha önce eklenmemiş. Download task çalıştırılacak. Yeni fonksiyon bu.")
        # download_image_for_product.delay(img_url, product.id)
        download_image_for_product.apply_async(args=[img_url_list[0], product.id], kwargs={}, queue='images')

    if product_created:
        return "%s veritabanına eklendi." % product.title
    else:
        return "%s update edildi." % product.title

