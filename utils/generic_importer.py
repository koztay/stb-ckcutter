import ast
from django.conf import settings
import json
from lxml import etree
from importer.models import ProductImportMap, ImporterFile
from importer.tasks import process_xml_row
# from my_importer.models import ImporterFile

# Importerlarımızın default_fields 'a erişebilmeleri için BaseImporter objesi yaratmalarına gerek olmasın diye
# class 'ın dışında aşağıdaki gibi global olarak tanımladık.


def drop_xml_element_by_word(func):
    def func_wrapper(*args, **kwargs):
        root = func(*args, **kwargs)
        word_list = kwargs.get('dropping_words')
        # print("bu funk çalışıyor mu abooovv")
        # print(word_list)
        if word_list:
            # create xpath
            # check every filtered words
            for dictionary in word_list:
                words = dictionary.get("words")
                field = dictionary.get("field")  # burada field yerine xpath gönder
                # create a new list contains the filtered records
                # Aşağıdaki liste sadece Baslik taglerinin listesi
                list_of_elements = [bad.getparent() for bad in root.xpath(field) if
                                    any(word in bad for word in words)]
                # print(list_of_elements)
                # for element in list_of_elements:
                #     print(element.text)

                # Aşağıda da bir üste çıkıp getparent() ile "Urun" tagine ulaşıyoruz ve remove ediyoruz.
                [root.remove(element.getparent()) for element in list_of_elements]
        return root
    return func_wrapper


def search_and_replace(func):
    def func_wrapper(*args, **kwargs):
        root = func(*args, **kwargs)
        word_list = kwargs.get('replacing_words')

        if word_list:
            # create xpath
            # check every filtered words
            for dictionary in word_list:
                words = dictionary.get("words")
                # print("WORDS :", words)
                field = dictionary.get("field")  # burada field yerine xpath gönder
                # print("FIELD :", field)
                for word in words:
                    for item in root.xpath(field):
                        parent = item.getparent()
                        parent.text = item.replace(str(word[0]), str(word[1]))
        return root
    return func_wrapper


class BaseParser:
    def __init__(self, file_path, xpath_for_products, dropping_words, replacing_words):
        """
        This class is base class for the xml file or excel file to be imported. It parses the source and sends the row
        objects to the BaseImporter class.
        :param file_path:
        :param xpath_for_products: it is a string object like ".//Urun"
        :param dropping_words: the list of dictionary objects as the following:
        drop_words=[{"words": ("PANASONIC", "panasonic", "Panasonic", "perdesi", "Perdesi"),
                    "field": "//Urun/Baslik/node()"}]
        :param replacing_words: list of dictionary objects as the following:
        replace_words=[{"words": [("Projeksiyon", "MMmrojeksşyon"), ("Perde", "Merde")],
                        "field": "//Urun/Baslik/node()"
                        }]
        """
        self.file_path = file_path  # this will come from the model object (could be local or remote path)
        self.xpath_for_products = xpath_for_products
        self.dropping_words = dropping_words  # this will come from the model object
        self.replacing_words = replacing_words  # this will come from the model object

    # We want to make process_file function must be implemented on the descendants, so we raise NotImplementedError
    def process_file(self, *args, **kwargs):
        raise NotImplementedError('subclasses of BaseParser must Implement process_file() method')


class XMLParser(BaseParser):
    @search_and_replace
    @drop_xml_element_by_word
    def process_file(self, *args, **kwargs):
        parser = etree.XMLParser(strip_cdata=False, recover=True)
        doc = etree.parse(self.file_path, parser)
        root = doc.getroot()
        # print("xpath ney layn :", self.xpath_for_products)
        # result = len(root.xpath(self.xpath_for_products))
        # print("filter_öncesi xml: ", result)
        return root


class BaseImporter:
    # default_fields tek bir merkezden yönetilir böylece...

    def __init__(self, map_obj, xml_document, xpath_for_products):
        """

        :param default_db_fields: a dictionary object of the minimum fields to create product record.
        :param row_object: a dictionary or xml object contains single product with default fields.
        will be replaced in product title.
        """
        self.map_obj = map_obj
        self.xml_document = xml_document  # this dict will come from importer or my_importer (Ancak row 'lar dict_olarak
        # gelmeyebilir). O nedenle bunu row object olarak adlandırdım.
        # self.dropping_words = dropping_words  # this will come from the model object
        # self.replacing_words = replacing_words
        self.xpath_for_products = xpath_for_products

    def yield_elements(self):
        for node in self.xml_document.xpath(self.xpath_for_products):
            yield node

    # bu func 'ı task olarak çalıştıracağız bence. Ama dur hemen netleşmedi daha
    def process_row_object(self):
        """
        This function is responsible for processign the rows dictionary and filters it against dropping_words etc.
        :return: "Filtered dictionary or a record with process_row() function which is not created yet. Did not decided
        yet. Maybe the best thing is to return a generator object by using yield"
        """
        # row_object = []

        for element in self.yield_elements():
            row_object = []
            # print(element.xpath(".//Baslik/node()")[0])
            for map_item in self.map_obj.fields_set.all():
                # eşleştirmede boş bırakılmamış olanları al
                if map_item.xml_field:
                    # dictionary olarak değerlendirebilmek için eval ile çekmeliyiz:
                    xml_field_as_dictionary = ast.literal_eval(map_item.xml_field)
                    # print(xml_field_as_dictionary)
                    model, field = self.get_model_field_for_row_value(value=map_item.product_field)  # it is a tuple
                    # print("model :", model)
                    value = self.get_value_for_field(field=map_item.xml_field, element=element)
                    # print("value :", value)
                    row_object.append({"model": model, "field": field, "value": value})
                    if field is "Aciklama":
                        print("Açıklama fieldını buldum... Value neymiş?")
                        # print(value)
            # row_object.append(product_field_list)
            yield row_object
                # print(element.xpath(map_item.xml_field))
                # print(map_item.product_field, map_item.xml_field)
                # print("model :", settings.DEFAULT_FIELDS.get(map_item.product_field).get("model"))
        # row_element = kwargs.get("row_element")
        # print(row_element.xpath(".//Urun/Baslik/node()"))
        # şimdilik sadece dropping word 'leri yazsın yeter.
        # print(self.replacing_words)


        # for key in settings.DEFAULT_FIELDS:
        #     print(key)

    def get_model_field_for_row_value(self, *args, **kwargs):
        """
        This is a helper function for process_row_object
        :param value:
        :return: Returns a tuple as (model, local_field)
        """
        default_fields = settings.DEFAULT_FIELDS
        product_field = kwargs.get('value')
        # print(product_field)
        return default_fields.get(product_field).get("model"), default_fields.get(product_field).get("local_field")
        # if default_field:
        #     return default_field.get('model'), default_field.get('local_field')
        # else:
        #     return None

    def update_db(self, number_of_items, create_allowed, download_images):

        for number, row in enumerate(self.process_row_object()):
            if number_of_items:
                if number < number_of_items:
                    # aşağıya print_row yerine add.delay(row) şeklinde bir task yazacağız.
                    # title = [d.get('value') for d in row if d.get('field') is 'title']
                    # print(title)
                    # print(len(title))
                    # process_xml_row(self, row=row)
                    json_values = json.dumps(row)

                    # print(json_values)
                    # process_xml_row(self, row=json_values)
                    # process_xml_object_oriented(self, row=json_values)
                    process_xml_row.apply_async(args=[], kwargs={'row': json_values,
                                                                 'create_allowed': create_allowed,
                                                                 'download_images': download_images,
                                                                 }, queue='xml')
                else:
                    break
            else:
                # title = list(filter(lambda key: key['title'], row))
                # title = [d for d in row if d.get('field') is 'baslik']
                # print(title)
                # process_xml_row(self, row=row)
                json_values = json.dumps(row)

                # print(json_values)
                process_xml_row.apply_async(args=[], kwargs={'row': json_values,
                                                             'create_allowed': create_allowed,
                                                             'download_images': download_images,
                                                             }, queue='xml')

    def get_value_for_field(self, field, element):
        raise NotImplementedError('subclasses of BaseImporter must Implement get_value_for_field() method')

    # Aşağıdaki şekilde field processing fonksiyonu ile process etsek daha mı iyi olur?
    def process_product_field(self):
        pass

    def process_variation_field(self):
        pass

    def process_category_field(self):
        pass

    def process_product_type_field(self):
        pass

    def process_currency_field(self):
        pass


class XMLImporter(BaseImporter):
    def get_value_for_field(self, field, element):
        # print("field: ", field)
        xml_field_as_dictionary = ast.literal_eval(field)
        xpath = xml_field_as_dictionary.get("xpath")
        default = xml_field_as_dictionary.get("default")
        if xpath:
            return element.xpath(xpath)
        elif default:
            return default
        else:
            return xml_field_as_dictionary


# TODO : in future change this func name to run_all_xml_steps and create another for run_all_xls_steps
def run_all_steps(**kwargs):
    xml_file_pk = kwargs.get("xml_file_pk")
    import_map_pk = kwargs.get("import_map_pk")
    number_of_items = kwargs.get("number_of_items")
    download_images = kwargs.get("download_images")
    allow_item_creation = kwargs.get("allow_item_creation")

    print(kwargs)

    import_map_obj = ProductImportMap.objects.get(pk=import_map_pk)
    xml_file_obj = ImporterFile.objects.get(pk=xml_file_pk)

    root_xpath = import_map_obj.root
    # print("root_xpath :", root_xpath)
    # ast.literal_eval("{'muffin' : 'lolz', 'foo' : 'kitty'}")
    # {'muffin': 'lolz', 'foo': 'kitty'}
    dropping_words_list = ast.literal_eval(import_map_obj.dropping_words)
    replace_words_list = ast.literal_eval(import_map_obj.replace_words)

    file_path = xml_file_obj.get_file_path()

    parser = XMLParser(file_path=file_path, xpath_for_products=root_xpath,
                       dropping_words=dropping_words_list, replacing_words=replace_words_list)

    filtered_xml_document = parser.process_file(dropping_words=parser.dropping_words,
                                                replacing_words=parser.replacing_words)

    my_importer = XMLImporter(map_obj=import_map_obj,
                              xml_document=filtered_xml_document,
                              xpath_for_products=root_xpath)
    my_importer.update_db(number_of_items=number_of_items,
                          create_allowed=allow_item_creation,
                          download_images=download_images)


