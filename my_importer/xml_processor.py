#!/usr/bin/python
# -*- coding: utf-8 -*-

# import xml.etree.ElementTree as etree #this is not preserve CDATA
import os
from lxml import etree

# dir_path = os.path.dirname(os.path.realpath(__file__))
# "/app/ecommerce_istebu_cookiecutter/media/my_importer/n11_urunler_fmjkb4d.xml"


def get_dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_root(file_path):
    """
    This function reads the file saved to teporary location by nginx e.g. /var/cache/nginx/client_temp/0000000001
    So, it works without any problem on first run. But it does not work properly after the file has been saved.
    :param file_path: instance.filepath 
    :return: 
    """
    print("I am printing the file path of file location: ", file_path)
    parser = etree.XMLParser(strip_cdata=False, recover=True)
    try:
        tree = etree.parse(file_path, parser)
    except etree.XMLSyntaxError:
        print('Skipping invalid XML from URL {}'.format(file_path))
        return

    # tree = etree.parse(file_path, parser)
    root = tree.getroot()
    # print(root.tag)  # Burada Urunler basması lazım.
    # print(root.getchildren()[0])  # root.getchildren() tüm ürünleri element olarak listeliyor. findall() 'a gerek yok.
    # print(root.getchildren()[0].tag) # bu da ilk elementin tagini veriyor.
    return root


def get_root_saved(file_path):
    print("I am printing the file path of saved location: ", file_path)
    with open(file_path) as f:
        data = f.read()
        parser = etree.XMLParser(strip_cdata=False, recover=True)
        tree = etree.parse(data, parser)
        root = tree.getroot()
    # print(root.tag)  # Burada Urunler basması lazım.
    # print(root.getchildren()[0])  # root.getchildren() tüm ürünleri element olarak listeliyor. findall() 'a gerek yok.
    # print(root.getchildren()[0].tag) # bu da ilk elementin tagini veriyor.
    return root


# buna gerek yok ben sub_elementlere bakıyorum ama dursun şimdilik bir zararı yok.
def get_all_elements(root):
    all_elements = list(root.iter())
    unique_tags = set([element.tag for element in all_elements])
    return unique_tags


def get_all_sub_elements_in_xml_root(root):
    for child in root:
        all_subs = list(child.iter())  # child.iter() yapınca alt elementleri de almamızı sağlıyor.
        return set([sub.tag for sub in all_subs])
        # for sub in child:
        #     print(sub.tag)


def get_all_sub_elements_as_dict(root):
    """
    returns the dictionary array of the products
    :param urunler: this is the all products as Element from root.getchildren()
    :return: 
    """
    urunler = root.getchildren()
    urunler_array = []
    for urun in urunler:
        all_sub_elements = list(urun.iter())
        urun_as_dictionary = dict()
        [urun_as_dictionary.update({sub.tag: sub.text}) for sub in all_sub_elements if not urun_as_dictionary.get(sub.tag)]
        urunler_array.append(urun_as_dictionary)
    return urunler_array



