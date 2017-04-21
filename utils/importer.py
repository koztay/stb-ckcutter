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


class BaseImporter(object):
    # default_fields tek bir merkezden yönetilir böylece...

    def __init__(self, default_db_fields, row_dict, dropping_words):
        self.default_db_fields = default_db_fields
        self.row_dict = row_dict  # this dict will come from importer or my_importer
        self.dropping_words = dropping_words  # this will come from the model object

    def process_row_dictionary(self):  # this will process the row maybe
        """
        This function is responsible from processign the row dictionary and insert or update the records to database.
        :return: "Updated or Inserted as text"
        """
        pass

    def get_model_field_for_row_value(self, value):
        """
        This is a helper function for process_row_dictionary
        :param value: 
        :return: Returns a tuple as (model, local_field)
        """
        default_field = self.default_db_fields.get(value)
        if default_field:
            return default_field.get('model'), default_field.get('local_field')
        else:
            return None
