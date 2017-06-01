from __future__ import absolute_import, unicode_literals
import json
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


class BaseDataImporterTask:

    def __init__(self, file_type, row, create_allowed, download_images):
        self.file_type = file_type
        if self.file_type == "XML":
            self.row = json.loads(row)
        else:
            self.row = row
        self.create_allowed = create_allowed
        self.download_images = download_images

    @staticmethod
    def _create_magazakodu(prefix, suffix, product_id):
        # print("gelen prefix ve suffix :")
        # print(prefix, suffix)
        kod_query_set = Product.objects.filter(istebu_product_no__icontains=prefix)
        # print(kod_query_set)
        product_instance = Product.objects.get(pk=product_id)
        # print("product_instance :", product_instance)
        if not product_instance.istebu_product_no:  # Eğer kod varsa girme, yoksa gir...
            if kod_query_set.count() > 0:
                kod_array = [int(kod.istebu_product_no[len(prefix):]) for kod in kod_query_set]
                last_number = max(kod_array)
                return prefix + str((last_number + 1))
            else:
                return prefix + str(suffix)
        else:
            return product_instance.istebu_product_no

    def _update_default_fields(self, product_instance=None):

        variation_instance = product_instance.variation_set.all()[0]  # product save edilince otomatik yaratılıyor.
        default_fields = settings.DEFAULT_FIELDS
        # default fileds models içerisinde tanımlı
        for main_field in default_fields:
            cell = self._get_value_for_field(main_field)
            # print(main_field, default_fields[main_field]["model"], cell)
            # print("value :", cell)

            # hücrenin Pruduct modelde mi, Variation modelde mi olduğunu bul
            cell_value_model = default_fields[main_field]["model"]
            # print("cell_value_model: ", cell_value_model)

            if cell_value_model is "Product":
                # print("attribute: ", default_fields[main_field]["local_field"])
                # print("value: ", cell)
                attribute = default_fields[main_field]["local_field"]
                if attribute == "istebu_product_no":
                    if isinstance(cell, dict):
                        if cell.get("prefix"):
                            prefix = cell.get("prefix")
                            suffix = cell.get("suffix")
                            magaza_kodu = self._create_magazakodu(prefix, suffix, product_instance.pk)
                            product_instance.istebu_product_no = magaza_kodu
                        else:
                            setattr(product_instance, attribute, cell)
                    else:
                        setattr(product_instance, attribute, cell)
                else:
                    setattr(product_instance, attribute, cell)
                    # setattr(product_instance, attribute, cell)

            elif cell_value_model is "Variation":
                # print("attribute: ", default_fields[main_field]["local_field"])
                # print("value: ", cell)
                setattr(variation_instance, default_fields[main_field]["local_field"], cell)

            elif cell_value_model is "ProductType":
                # product_type_name = default_fields[main_field]["local_field"]
                # print("product_type_name :", product_type_name)
                product_type_instance, created = ProductType.objects.get_or_create(name=cell)
                product_instance.product_type = product_type_instance

            elif cell_value_model is "AttributeValue":
                attributetype_instance = AttributeType.objects.get(type="Marka")
                attributetype_instance.product_type = product_instance.product_type  # burada ptoduc
                AttributeValue.objects.get_or_create(attribute_type=attributetype_instance,
                                                     product=product_instance,
                                                     value=cell)


            elif cell_value_model is "Currency":
                # print("attribute: ", default_fields[main_field]["local_field"])
                # print("Currency neden eşleşmiyor AMK?: ", cell)
                # Eğer currency veriatabanında yoksa o zaman ürünü ekleme. Dolayısıyla "Para Birimi" önceden eklenmeli.
                try:
                    currency_instance = Currency.objects.get(name=cell)
                    variation_instance.buying_currency = currency_instance
                except:
                    print("Currency bulunamadı, %s eklenmedi!" % product_instance.title)
                    pass

                    # print("variation_instance.buying_currency", variation_instance.buying_currency)

            elif cell_value_model is "Category":
                try:
                    category = Category.objects.get(title=cell)
                    # print("Kategori: ", category)
                    product_instance.categories.add(category)
                except:
                    print("Kategori bulunamadı lütfen ekleyin : ", cell)

            else:
                print("ProductImage dönmüş olması lazım => cell_value_model: ", cell_value_model)

        factor = float(settings.IMPORTER_SALE_PRICE_FACTOR)
        product_instance.price = float(variation_instance.sale_price) * factor

        # ürünlerin fiyatı boş geliyor o nedenle factor kadar yükseltiyoruz...
        product_instance.save()
        variation_instance.save()

    def _get_value_for_field(self, field_name):
        raise NotImplementedError("Subclasses of BaseDataImporterTask class must implement get_value_for_field method")

    def run_import_task(self):
        title = self._get_value_for_field("Urun_Adi")  # it is a list contains another list
        # print("title list mi kine acabağı?:", title)
        vendor_urun_kodu = self._get_value_for_field("Vendor_Urun_Kodu")  # bunu eşleştirdim.
        print("vendor kod :", self._get_value_for_field)

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

        self._update_default_fields(product_instance=product)
        # update_default_fields(product)  # her halükarda yaratılacak o yüzden önemsiz...

        if self.download_images:
            img_url_list = self._get_value_for_field("Urun_Resmi")
            # TODO: Şimdilik sadece tek resim alabiliyoruz. İleride düzelt.
            if product.productimage_set.all().count() == 0:  # image varsa boşu boşuna task ekleme.
                print("Resim daha önce eklenmemiş. Download task çalıştırılacak. Yeni fonksiyon bu.")
                # download_image_for_product.delay(img_url, product.id)
                download_image_for_product.apply_async(args=[img_url_list[0], product.id], kwargs={}, queue='images')

        if product_created:
            return "%s veritabanına eklendi." % product.title
        else:
            return "%s update edildi." % product.title


class XMLImporterTask(BaseDataImporterTask):

    def _get_value_for_field(self, field_name):
        db_field = settings.DEFAULT_FIELDS.get(field_name).get('local_field')  # bu tek başına saçmalatıyor...
        model = settings.DEFAULT_FIELDS.get(field_name).get('model')  # model de olmalı
        # print("db_field", db_field)
        value = [d.get('value') for d in self.row if d.get('field') == db_field and d.get('model') == model]

        if field_name is 'Urun_Resmi':
            return value
        else:
            if len(value) > 0:
                if isinstance(value[0], list):
                    return value[0][0]
                else:
                    return value[0]
            else:
                return None


class XLSImporterTesk(BaseDataImporterTask):
    def __init__(self, importer_map_pk, row_number, file_type, row, create_allowed, download_images):
        super().__init__(file_type, row, create_allowed, download_images)
        self.importer_map = ProductImportMap.objects.get(pk=importer_map_pk)
        self.row_number = row_number

    def _get_value_for_field(self, field_name):

        try:
            field_object = self.importer_map.fields_set.get(product_field=field_name)
            cell_value_index = field_object.get_xml_field()  # Adına get_xml_filed demişiz ama xls, xlsx için de aynısı.

            cell_value = self.row[int(cell_value_index)]  # field eşleştirmeleri 0,1,2 gibi indeks değeri ile yapıldığı
            # için sorun yok. Şimdilik indeks yerine hücreye ait başlık ile eşleştirme yapmayı çözemedim.
        except:
            cell_value = ""
        return cell_value


@task(bind=True, name="Download Image", rate_limit="40/h")
def download_image_for_product(self, image_link=None, product_id=None):
    result = "Hata! %s linkindeki resim indirilemedi:" % image_link
    try:
        result = image_downloader.download_image(image_link, product_id)
    except Exception as e:
        self.retry(countdown=120, exc=e, max_retries=2)

    return result


@task(bind=True, name="Process XML Row", rate_limit="120/m")
def process_xml_row(self, row=None, create_allowed=False, download_images=False):
    xml_task = XMLImporterTask(file_type="XML", row=row, create_allowed=create_allowed, download_images=download_images)
    return xml_task.run_import_task()


@task(bind=True, name="Process XLS Row", rate_limit="120/m")
def process_xls_row(self, importer_map_pk, row, values, create_allowed=False, download_images=False):
    xls_task = XLSImporterTesk(file_type="XLS", row=values, importer_map_pk=importer_map_pk, row_number=row,
                               create_allowed=create_allowed, download_images=download_images)
    return xls_task.run_import_task()

