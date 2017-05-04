# -*- coding: utf-8 -*-
from importer import XMLParser  # BU SALAK PYCHARM ALTINI ÇİZİYOR NEDENSE....


my_parser = XMLParser(file_path="n11_urunler2.xml", xpath_for_products=".//Urun",
                      dropping_words=[{"words": ("PANASONIC", "panasonic", "Panasonic", "perdesi", "Perdesi"),
                                       "field": "//Urun/Baslik/node()"}],
                      replacing_words=[{"words": ("Projeksiyon", "MMmrojeksşyon"), "field": "//Urun/Baslik/node()"}])

my_document = my_parser.process_file(dropping_words=my_parser.dropping_words, replacing_words=my_parser.replacing_words)
# my_row_handler = RowHandler(parser=my_parser)
# my_root = my_row_handler.process_xml(drop_words=my_parser.drop_words, replace_words=my_parser.replace_words)
#
result = len(my_document.xpath(".//Urun"))
print("filter_sonrası xml: ", result)
#
for item in my_document.xpath("//Urun/Baslik/node()"):
    print(item)
