from django.views.generic.base import TemplateView
# from_valid metodunu override edersek aşağıdakiler gerekiyor
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType  # bu neden gerekli?
from data_importer.models import FileHistory


from data_importer.views import DataImporterForm
from data_importer.importers import XMLImporter, GenericImporter  # ileride XMLImporterı da kaldırabilirsek süper olur.
from products.models import Product, ProductType, Currency, Variation, AttributeType, AttributeValue, Category, ProductImage
from products.mixins import StaffRequiredMixin

from .forms import ProductImporterMapTypeForm, ProductXMLImporterMapRootValueForm
from .models import ProductImportMap, default_fields
from .tasks import process_xls_row, download_image_for_product

# https://www.youtube.com/watch?v=z0Gxxjbos4k linkinde anlatmış nasıl yapıldığını
# from pycharmdebug import pydevd


# Aşağıdaki no_task fonksiyonu ile import edebiliyoruz.
def process_xls_row_no_task(importer_map_pk, row, values):
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
        for main_field in default_fields:
            cell = get_cell_for_field(main_field)
            print("cell_value :", cell)
            cell_value_model = default_fields[main_field]["model"]
            print("cell_value_model: ", cell_value_model)

            if cell_value_model is "Product":
                print("attribute: ", default_fields[main_field]["field"])
                print("value: ", cell)
                attribute = default_fields[main_field]["field"]
                if attribute is 'categories':
                    pass
                else:
                    setattr(product_instance, attribute, cell)

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
                except:
                    print("Currency bulunamadı, %s eklenmedi!" % product.title)
                    pass
                variation_instance.buying_currency = currency_instance
                print("variation_instance.buying_currency", variation_instance.buying_currency)

            else:
                print("Hata! Böyle bir model dönmemeli, cell_value_model: ", cell_value_model)
        product_instance.price = variation_instance.sale_price  # ürünlerin fiyatı boş geliyor o nedenle...
        product_instance.save()
        variation_instance.save()

    title = get_cell_for_field("Ürün Adı")
    # product_type = ProductType.objects.get(name=importer_map.type)
    product, product_created = Product.objects.get_or_create(title=title)

    update_default_fields(product_instance=product)
    # update_default_fields(product)  # her halükarda yaratılacak o yüzden önemsiz...

    img_url = get_cell_for_field("Image")

    # aşağıdaki fonsiyon da import ediyor ürünleri sorunsuz şekilde...
    print("IMG URL => :", img_url)
    download_image_for_product.delay(img_url, product.id)
    return "%s update edildi." % product.title


# /data-importer/import/ linkinde
# @staff_member_required
class ImporterHomePageView(StaffRequiredMixin, TemplateView):
    template_name = "importer/importer_list.html"


class ProductGenericImporter(GenericImporter):
    class Meta:
        model = Product
        ignore_first_line = True

    # process row'u override edeceğiz. kendi importerımı kendim yazıyorum.
    # TODO: Burada her Row 'u process ederken task olarak Celery queue 'ye ekle.
    def process_row(self, row, values):
        importer_map = ProductImportMap.objects.get(pk=self.importer_type)
        # process_xls_row_no_task(importer_map.pk, row, values)
        process_xls_row.delay(importer_map_pk=importer_map.pk, row=row, values=values)


class GenericImporterCreateView(StaffRequiredMixin, DataImporterForm):

    template_name = 'importer/product_importer.html'
    extra_context = {'title': 'Select File for Data Importer',
                     'template_file': 'myfile.xls',
                     'success_message': "File uploaded successfully",
                     }
    importer = ProductGenericImporter

    def get_context_data(self, **kwargs):
        context = super(GenericImporterCreateView, self).get_context_data(**kwargs)
        importer_type_form = ProductImporterMapTypeForm(self.request.POST or None)
        context['importer_type_form'] = importer_type_form
        return context

    def form_valid(self, form, owner=None):
        selected_import_map_id = self.request.POST.get('import_map')  # import map seçebilmek için.
        self.importer.importer_type = selected_import_map_id

        if self.request.user.id:
            owner = self.request.user

        if self.importer.Meta.model:
            content_type = ContentType.objects.get_for_model(self.importer.Meta.model)
            file_history, _ = FileHistory.objects.get_or_create(file_upload=form.cleaned_data['file_upload'],
                                                                owner=owner,
                                                                content_type=content_type)
        # Bu satırı celery 'yi dikkate almaması için yazdık.
        self.is_task = False
        if not self.is_task or not hasattr(self.task, 'delay'):
            self.task.run(importer=self.importer,
                          source=file_history,
                          owner=owner,
                          send_email=False)
            if self.task.parser.errors:
                messages.error(self.request, self.task.parser.errors)
            else:
                messages.success(self.request,
                                 self.extra_context.get('success_message', "File uploaded successfully"))
        else:
            self.task.delay(importer=self.importer, source=file_history, owner=owner)
            if owner:
                messages.info(
                    self.request,
                    "When importer was finished one email will send to: {0!s}".format(owner.email)
                )
            else:
                messages.info(
                    self.request,
                    "Importer task in queue"
                )

        return super(DataImporterForm, self).form_valid(form)

