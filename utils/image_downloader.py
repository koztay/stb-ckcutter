# coding=utf-8
import os
import shutil
import random
import urllib3

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File

from products.models import ProductImage, Product

download_url = 'http://i.hurimg.com/i/hurriyet/75/892x220/58a9fa28c03c0e20402a9064.jpg'

'http://images.hepsiburada.net/assets/Mobilya/500/9443499868210.jpg'
# new_product = Product.objects.create(title='yeni ürün 1')
# result = download_image(download_url, new_product)
"""
image_upload_to 'dan kaynaklanan aynı title 'da iki ürün varsa o zaman main_image'ları ilk product altına koyuyor.
Ancak main image 'ları biz sitede kullanmıyoruz sanırım. Thumbnailler için ayrı klasör yaratıyor. Main image farklı
isimde ilk ürünün klasöründe kalıyor. Çünkü image_upload_to bu şekilde yapılmış.
"""


def download_image(url, product_id):
    print("indirilecek resim linki :", url)
    product = Product.objects.get(pk=product_id)
    try:
        product_image = product.images.get(remote_url=url)
        return "Product image exist for %s and for remote url: %s" % (product.title, product_image.remote_url)
    except ObjectDoesNotExist:
        # product image does not exist, therefore download image
        filename = url.split('/')[-1]
        print('file_name', filename)
        # create temp location
        temp_loc = "%s/%s/tmp" % (settings.MEDIA_ROOT + "/products", product.slug)
        print("temp_loc : %s" % temp_loc)
        if not os.path.exists(temp_loc):
            print("temp_location does not exists")
            os.makedirs(temp_loc)
        temp_file_path = os.path.join(temp_loc, filename)
        if os.path.exists(temp_file_path):
            print("temp_location exists")
            temp_path = os.path.join(temp_loc, "%s" % (random.random()))
            os.makedirs(temp_path)
            temp_file_path = os.path.join(temp_path, filename)

        http = urllib3.PoolManager()
        with http.request('GET', url, preload_content=False) as resp, \
                open(temp_file_path, 'wb') as out_file:
            if resp.status is 200:
                shutil.copyfileobj(resp, out_file)
            else:
                raise ValueError('A very specific bad thing happened. Response code was not 200')

        product_image_data = open(temp_file_path, "rb")
        product_image_file = File(product_image_data)
        product_image = ProductImage.objects.create(product=product)
        product_image.remote_url = url
        product_image.image.save(os.path.basename(temp_file_path), product_image_file)
    return "Product image downloaded for %s" % product.title






