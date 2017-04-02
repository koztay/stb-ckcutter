#!/usr/bin/python
# -*- coding: utf-8 -*-

# import xml.etree.ElementTree as etree #this is not preserve CDATA
from lxml import etree


def get_root(file_path):
    parser = etree.XMLParser(strip_cdata=False, recover=True)
    tree = etree.parse(file_path, parser)
    root = tree.getroot()
    return root


def get_all_elements(root):
    all_elements = list(root.iter())
    unique_tags = set([element.tag for element in all_elements])
    return unique_tags


# Aşağıdaki çalışıyor...
def change_price(manufacturer=None, increase_factor=None):
    for product in root.findall('Urun'):
        product_name = product.find('Baslik').text
        for manufacturer_name in manufacturer:
            if manufacturer_name in product_name:
                sub_element = product.find('Fiyat')
                old_price = float(sub_element.text)
                new_price = math.ceil(old_price * increase_factor)
                new_element = etree.Element("Fiyat")
                new_element.text = etree.CDATA(str(new_price))
                product.replace(sub_element, new_element)
                print(product_name, old_price, new_price)


def increase_price_for_all(increase_factor=None):
    for product in root.findall('Urun'):
        product_name = product.find('Baslik').text
        sub_element = product.find('Fiyat')
        old_price = float(sub_element.text)
        new_price = math.ceil(old_price * increase_factor)
        new_element = etree.Element("Fiyat")
        new_element.text = etree.CDATA(str(new_price))
        product.replace(sub_element, new_element)
        print(product_name, old_price, new_price)


def remove_product(manufacturer=None):
    print(manufacturer)
    for product in root.findall('Urun'):
        product_name = product.find('Baslik').text
        for manufacturer_name in manufacturer:
            print
            manufacturer_name
            if manufacturer_name in product_name:
                root.remove(product)


def adjust_resolutions():
    # the following loop works for resolution
    for Gercek_Cozunurluk in root.iter('Gercek_Cozunurluk'):
        new_cozunurluk = Gercek_Cozunurluk.text.replace("x", " x ")
        Gercek_Cozunurluk.text = etree.CDATA(new_cozunurluk)


def adjust_lamplifes():
    for Lamba_Omru in root.iter('Lamba_Omru'):
        old_lamp_life = Lamba_Omru.text.lower()
        # print (old_lamp_life)
        old_lamp_life = old_lamp_life.replace(" saat", "")
        old_lamp_life = int(old_lamp_life)

        if old_lamp_life < 3000:
            # set new lamp_life according to the checks
            new_lamp_life = "1.000_3.000 saat"
            Lamba_Omru.text = etree.CDATA(new_lamp_life)

        if 3000 <= old_lamp_life < 5000:
            # set new lamp_life according to the checks
            new_lamp_life = "3.000_5.000 saat"
            Lamba_Omru.text = etree.CDATA(new_lamp_life)

        if 5000 <= old_lamp_life < 10000:
            # set new lamp_life according to the checks
            new_lamp_life = "5.000_10.000 saat"
            Lamba_Omru.text = etree.CDATA(new_lamp_life)

        if 10000 <= old_lamp_life < 20000:
            # set new lamp_life according to the checks
            new_lamp_life = "10.000_20.000 saat"
            Lamba_Omru.text = etree.CDATA(new_lamp_life)

        if 20000 <= old_lamp_life <= 30000:
            # set new lamp_life according to the checks
            new_lamp_life = "20.000_30.000 saat"
            Lamba_Omru.text = etree.CDATA(new_lamp_life)

        if old_lamp_life > 30000:
            # set new lamp_life according to the checks
            new_lamp_life = "30.000 saatten fazla"
            Lamba_Omru.text = etree.CDATA(new_lamp_life)


def adjust_ekstra_features():
    for product in root.findall('Urun'):
        try:
            ekstra = product.find('Ekstra_Ozellikler').text

            three_d = etree.Element("ThreeDimension")
            product.append(three_d)

            kablosuz = etree.Element("Wireless")
            product.append(kablosuz)

            if "3d" in ekstra:
                three_d.text = 'VAR'
            else:
                three_d.text = 'YOK'

            if "kablosuz" in ekstra:
                kablosuz.text = 'VAR'
            else:
                kablosuz.text = 'YOK'

        except:
            three_d = etree.Element("ThreeDimension")
            product.append(three_d)
            three_d.text = 'YOK'

            kablosuz = etree.Element("Wireless")
            product.append(kablosuz)
            kablosuz.text = 'YOK'

        three_d.text = etree.CDATA(three_d.text)
        kablosuz.text = etree.CDATA(kablosuz.text)


def apply_changes():
    etree.tostring(root)

    tree.write(file_path + "n11_urunler.xml",
               pretty_print=True,
               xml_declaration=True,
               encoding="utf-8")

# Increase Viewsonics
# for product in root.findall('Urun'):
# 	product_name = product.find('Baslik').text
# 	if any(["Viewsonic" in product_name, "VİEWSONIC" in product_name, "VIEWSONIC" in product_name]):
# 		change_price(product=product, increase_factor=1.06)


# #Remove Epsons
# for product in root.findall('Urun'):
# 	product_name = product.find('Baslik').text
# 	if any(["Epson" in product_name, "EPSON" in product_name]):
# 		root.remove(product)
# remove_product(manufacturer = ["Epson", "EPSON"])

