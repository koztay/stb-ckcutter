# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
#
import json
from django.shortcuts import render, redirect
# from formtools.wizard.views import SessionWizardView
from tempfile import TemporaryFile

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import TemplateView, FormView, View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView, CreateView

from .forms import XMLFileMappingForm, ImporterFileForm, ImporterXMLSelectionForm, ImporterMapSelectionForm
from .models import XMLImportMap, ImporterFile
from .xml_processor import get_root, get_all_sub_elements_in_xml_root
from .tasks import run_all_steps
from utils.importer import default_fields


# Create your views here.
# DEFAULT_PRODUCT_FIELDS
# default_fields = {
#     "IGNORE": {"model": "NA", "local_field": "NA"},
#     "Magaza_Kodu": {"model": "Variation", "local_field": "istebu_product_no"},
#     "Vendor_Urun_Kodu": {"model": "Variation", "local_field": "vendor_product_no"},  # urun eşleşmesi bu kod ile
#     "Kategori": {"model": "Category", "local_field": "categories"},  # product.categories olarak eklenecek !!!!
#     "Alt_Kategori": {"model": "Category", "local_field": "categories"},  # product.categories olarak eklenecek !!!
#     "Urun_Tipi": {"model": "ProductType", "local_field": "name"},  # product.product_type olarak ekle !!!
#     "Marka": {"model": "AttributeValue", "local_field": "value"},  # value for AtrributeType.type == "Marka"
#     "Urun_Adi": {"model": "Product", "local_field": "title"},
#     "Aciklama": {"model": "Product", "local_field": "description"},
#     "Stok": {"model": "Variation", "local_field": "inventory"},
#     "KDV": {"model": "Product", "local_field": "kdv"},
#     "Para_Birimi": {"model": "Currency", "local_field": "name"},  # variation.buying_currency olarak ekle!!!
#     "Alis_Fiyati": {"model": "Variation", "local_field": "buying_price"},
#     "Satis_Fiyati": {"model": "Variation", "local_field": "sale_price"},
#     "Barkod": {"model": "Variation", "local_field": "product_barkod"},
#     "Kargo": {"model": "NA", "local_field": "NA"},
#     "Urun_Resmi": {"model": "ProductImage", "local_field": "image"},
# }

"""
    # yukarıdaki default field 'ı related products için gerekli. Algoritmayı incelemedim ama daha
    # iyi bir yol bulunabilir. // TODO: Bu field 'a gerek olmayacak şekilde düzenleme yap.
    slug = models.SlugField(blank=True, unique=True, max_length=1000)  # unique=True)
    show_on_homepage = models.BooleanField(default=True)
    show_on_popular = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)
    # taggable manager ile ilgili bir hata veriyor test edilemiyor.
    kdv = models.FloatField(default=18.0)
    desi = models.IntegerField(default=1)
"""


# step - 1 - Dosyayı Upload etmemizi sağlıyor.
def xml_upload_view(request):
    if request.method == 'POST':
        form = ImporterFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()  # commit=False yapınca henüz dosyayı yazmamış oluyor.
            file_path = instance.get_file_path()
            print("upload ettiğimde çalışan file path :", file_path)
            root = get_root(file_path=file_path)
            all_xml_tags = get_all_sub_elements_in_xml_root(root=root)
            # print(len(all_xml_tags))
            request.session["importer_name"] = instance.description
            request.session["XML_Root"] = ""
            request.session["total_xml_tag_count"] = len(all_xml_tags)  # set object has no attribute count
            request.session["xml_file_pk"] = instance.pk
            for i, tag in enumerate(all_xml_tags):
                request.session['tag'+str(i)] = tag
            return redirect('xml_map')
    else:
        form = ImporterFileForm()
    return render(request, 'my_importer/xml-select.html', {
        'form': form
    })


# step - 2 - Upload edilen dosyayı map etmemizi sağlıyor. Ancak buna gerek yok.
def xml_map_view(request):
    xml_tag_count = request.session.get('total_xml_tag_count')
    xml_elements = []
    for i in range(xml_tag_count):
        xml_elements.append(request.session.get('tag'+str(i)))
    default_locals = default_fields.keys()
    print(default_locals)
    # default_locals.append('Ignore')
    form = XMLFileMappingForm(request.POST or None, extra=xml_elements)

    if form.is_valid():
        data = default_fields  # bizim defaultumuzu yükleyip üzerine XML_Field ları yazıyoruz.
        for (xml_field, local_field) in form.extra_answers():
            data[local_field]['XML_Field'] = xml_field
        json_data = json.dumps(data)

        # create XMLImportMap from json_data here
        xml_import_map = XMLImportMap.objects.create(name=request.session.get('importer_name'), map=json_data)

        xml_file_pk = request.session.get("xml_file_pk")
        xml_file = ImporterFile.objects.get(pk=xml_file_pk)
        xml_file.import_map = xml_import_map
        xml_file.save()
        print("xml_file_pk", xml_file_pk)

        # start long running import task here... # sadece burada yeni ürün yaratmaya izin veriyoruz. remote çekimde yok.
        run_all_steps.delay(xml_file_pk, True)

        return redirect("home")

    return render(request, "my_importer/xml-map.html", {'form': form, })


# aşağıdakinde de manual çalışma yapıyoruz ve yeni ürün eklemeye izin veriyoruz.
class TaskRunnerView(FormView):
    template_name = 'my_importer/start_task.html'
    form_class = ImporterXMLSelectionForm
    success_url = '.'

    def form_valid(self, form, owner=None):
        xml_file_instance = form.cleaned_data.get('import_map')
        print(xml_file_instance.pk)
        file_instance = ImporterFile.objects.get(pk=xml_file_instance.pk)
        xml_map_instance = file_instance.import_map
        print(xml_map_instance)
        print(xml_map_instance.pk)
        run_all_steps.delay(xml_file_instance.pk, True)
        return super(TaskRunnerView, self).form_valid(form)



















