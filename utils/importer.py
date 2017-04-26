from lxml import etree
# Importerlarımızın default_fields 'a erişebilmeleri için BaseImporter objesi yaratmalarına gerek olmasın diye
# class 'ın dışında aşağıdaki gibi global olarak tanımladık.

default_fields = {
    "IGNORE": {"model": "NA", "local_field": "NA"},
    "Magaza_Kodu": {"model": "Variation", "local_field": "istebu_product_no"},
    "Vendor_Urun_Kodu": {"model": "Variation", "local_field": "vendor_product_no"},  # urun eşleşmesi bu kod ile olacak
    "Kategori": {"model": "Category", "local_field": "categories"},  # product.categories olarak eklenecek !!!!
    "Alt_Kategori": {"model": "Category", "local_field": "categories"},  # product.categories olarak eklenecek !!!
    "Urun_Tipi": {"model": "ProductType", "local_field": "name"},  # product.product_type olarak ekle !!!
    "Marka": {"model": "AttributeValue", "local_field": "value"},  # value for AtrributeType.type == "Marka"
    "Urun_Adi": {"model": "Product", "local_field": "title"},
    "Aciklama": {"model": "Product", "local_field": "description"},
    "Stok": {"model": "Variation", "local_field": "inventory"},
    "KDV": {"model": "Product", "local_field": "kdv"},
    "Para_Birimi": {"model": "Currency", "local_field": "name"},  # variation.buying_currency olarak ekle!!!
    "Alis_Fiyati": {"model": "Variation", "local_field": "buying_price"},
    "Satis_Fiyati": {"model": "Variation", "local_field": "sale_price"},
    "N11_Satis_Fiyati": {"model": "Variation", "local_field": "n11_price"},
    "GG_Satis_fiyati": {"model": "Variation", "local_field": "gittigidiyor_price"},
    "Barkod": {"model": "Variation", "local_field": "product_barkod"},
    "Kargo": {"model": "NA", "local_field": "NA"},
    "Urun_Resmi": {"model": "ProductImage", "local_field": "image"},
}


def drop_xml_element_by_word(func):
    def func_wrapper(*args, **kwargs):
        root = func(*args, **kwargs)
        word_list = kwargs.get('dropping_words')
        print("bu funk çalışıyor mu abooovv")
        print(word_list)
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
                print(words)
                field = dictionary.get("field")  # burada field yerine xpath gönder
                # for word in words:
                for item in root.xpath(field):
                    parent = item.getparent()
                    parent.text = item.replace(words[0], words[1])
        return root
    return func_wrapper


class BaseParser(object):
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
        raise NotImplementedError('Implement process_file() method for your parser')


class XMLParser(BaseParser):
    @search_and_replace
    @drop_xml_element_by_word
    def process_file(self, *args, **kwargs):
        parser = etree.XMLParser(strip_cdata=False, recover=True)
        doc = etree.parse(self.file_path, parser)
        root = doc.getroot()
        # result = len(root.xpath(self.xpath_for_products))
        # print("filter_öncesi xml: ", result)
        return root


class BaseImporter(object):
    # default_fields tek bir merkezden yönetilir böylece...

    def __init__(self, default_db_fields, row_object):
        """
        
        :param default_db_fields: a dictionary object of the minimum fields to create product record.
        :param row_object: a dictionary or xml object contains single product with default fields. 
        will be replaced in product title.
        """
        self.default_db_fields = default_db_fields
        self.row_object = row_object  # this dict will come from importer or my_importer (Ancak row 'lar dict_olarak
        # gelmeyebilir). O nedenle bunu row object olarak adlandırdım.
        # self.dropping_words = dropping_words  # this will come from the model object
        # self.replacing_words = replacing_words

    def process_row_object(self, *args, **kwargs):
        """
        This function is responsible for processign the rows dictionary and filters it against dropping_words etc.
        :return: "Filtered dictionary or a record with process_row() function which is not created yet. Did not decided
        yet. Maybe the best thing is to return a generator object by using yield"
        """
        # print(self.dropping_words)  # şimdilik sadece dropping word 'leri yazsın yeter.
        # print(self.replacing_words)
        pass

    def get_model_field_for_row_value(self, *args, **kwargs):
        """
        This is a helper function for process_row_object
        :param value: 
        :return: Returns a tuple as (model, local_field)
        """
        default_field = kwargs.get('value')
        if default_field:
            return default_field.get('model'), default_field.get('local_field')
        else:
            return None
