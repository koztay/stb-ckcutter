# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
#
import json
from django.shortcuts import render, redirect
# from formtools.wizard.views import SessionWizardView
from tempfile import TemporaryFile

from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from .forms import XMLFileMappingForm, ImporterFileForm
from .models import XMLImportMap
from .xml_processor import get_root, get_all_sub_elements_in_xml_root

# Create your views here.
# DEFAULT_PRODUCT_FIELDS
default_fields = {
    "IGNORE": {"model": "NA", "local_field": "NA"},
    "Magaza_Kodu": {"model": "Variation", "local_field": "istebu_product_no"},
    "Kategori": {"model": "Category", "local_field": "categories"},  # product.categories olarak eklenecek !!!!
    "Alt_Kategori": {"model": "Category", "local_field": "categories"}, # product.categories olarak eklenecek !!!
    "Urun_Tipi": {"model": "ProductType", "local_field": "name"},  # product.product_type olarak ekle !!!
    "Urun_Adi": {"model": "Product", "local_field": "title"},
    "KDV": {"model": "Product", "local_field": "kdv"},
    "Para_Birimi": {"model": "Currency", "local_field": "name"},  # variation.buying_currency olarak ekle!!!
    "Alis_Fiyati": {"model": "Variation", "local_field": "buying_price"},
    "Satis_Fiyati": {"model": "Variation", "local_field": "sale_price"},
    "Barkod": {"model": "Variation", "local_field": "product_barkod"},
    "Kargo": {"model": "NA", "local_field": "NA"},
    "Urun_Resmi": {"model": "ProductImage", "local_field": "image"},
}

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


# step - 1
def xml_upload_view(request):
    if request.method == 'POST':
        form = ImporterFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()  # commit=False yapınca henüz dosyayı yazmamış oluyor.
            file_path = instance.get_file_path()
            root = get_root(file_path=file_path)
            all_xml_tags = get_all_sub_elements_in_xml_root(root=root)
            # print(len(all_xml_tags))
            request.session["importer_name"] = instance.description
            request.session["XML_Root"] = ""
            request.session["total_xml_tag_count"] = len(all_xml_tags)  # set object has no attribute count
            for i, tag in enumerate(all_xml_tags):
                request.session['tag'+str(i)] = tag
            return redirect('xml_map')
    else:
        form = ImporterFileForm()
    return render(request, 'my_importer/xml-select.html', {
        'form': form
    })


# step - 2
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
        XMLImportMap.objects.create(name=request.session.get('importer_name'), map=json_data)

        # start long running import task here...

        return redirect("home")

    return render(request, "my_importer/xml-map.html", {'form': form, })























