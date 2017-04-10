import math

import urllib3
from django.conf import settings
from django.core.files import File
import os
import shutil
from PIL import Image
import random


def create_new_thumb(media_path, instance, owner_slug, max_width, max_height):
    if media_path.startswith("http"):
        print("I will download the file and use it as local")
        temporary_download_location = settings.STATIC_ROOT + "/tmp"
        filename = media_path.split("/")[-1]
        temporary_download_path = temporary_download_location + filename
        print(temporary_download_path)

        # create tmp directory if not exists
        if not os.path.exists(temporary_download_location):
            os.makedirs(temporary_download_location)

        if not os.path.exists(temporary_download_path):  # eğer file indirilmemişse indir.
            # download the file
            http = urllib3.PoolManager()
            with http.request('GET', media_path, preload_content=False) as resp, open(temporary_download_path, 'wb') as out_file:
                if resp.status is 200:
                    shutil.copyfileobj(resp, out_file)
                else:
                    raise ValueError('A very specific bad thing happened. Response code was not 200')

        # call the create new thumb func with new media path
        create_new_thumb_local(temporary_download_path, instance, owner_slug, max_width, max_height)
    else:
        create_new_thumb_local(media_path, instance, owner_slug, max_width, max_height)


def create_new_thumb_local(media_path, instance, owner_slug, max_width, max_height):
    filename = os.path.basename(media_path)
    filename = str(max_width) + "x" + str(max_height) + "-" + filename  # hep aynı isimde yazıyor yoksa
    print("filename : %s" % filename)
    thumb = Image.open(media_path)
    width, height = thumb.size
    # size = (max_height, max_width)
    # aspect_ratio = width / height

    # if width < max_width and height < max_height:  # her ikisi de kısa ise
    #     # hangi tarafa doğru genişletmek gerek bul
    #     if width / max_width < height / max_height:  # enden genişleyecek, boydan kırpılacak
    #         # print("her ikisi de kısa, enden genişleyecek, boydan kırpılacak")
    #         thumb = enden_genislet_boydan_kirp(width, height, max_width, max_height, thumb)
    #     else:  # boydan genişleyecek, enden kırpılacak
    #         # print("her ikisi de kısa, boydan genişleyecek, enden kırpılacak")
    #         thumb = boydan_genislet_enden_kirp(width, height, max_width, max_height, thumb)
    # elif width < max_width and height >= max_height:  # en küçük boy değil
    #     # print("en kısa boy değil, enden genişleyecek, boydan kırpılacak")
    #     thumb = enden_genislet_boydan_kirp(width, height, max_width, max_height, thumb)
    # elif width >= max_width and height < max_height:  # boy küçük en değil
    #     # print("boy kısa en değil, boydan genişleyecek, enden kırpılacak")
    #     thumb = boydan_genislet_enden_kirp(width, height, max_width, max_height, thumb)
    # elif width >= max_width and height >= max_height:  # her ikisi de büyük o yüzden resize yok.
    #     # print("her ikisi de büyük o yüzden resize yok. Bu hatalı resize olacak yine")
    #     if width / max_width > height / max_height:  # enden kırpılacak
    #         # print("enden kırparak thumb yarat.")
    #         thumb = enden_kirparak_thumb_yarat(width, height, max_width, max_height, thumb)
    #     elif width / max_width < height / max_height:
    #         # print("boydan kırparak thumb yarat.")
    #         thumb = boydan_kirparak_thumb_yarat(width, height, max_width, max_height, thumb)
    #     else:
    #         new_size = (max_width, max_height)
    #         thumb.thumbnail(new_size, Image.ANTIALIAS)
    #         # print(thumb)

    # thumb = auto_resize_and_crop_image(width, height, max_width, max_height, thumb)
    thumb = auto_resize_without_crop(width, height, max_width, max_height, thumb)

    temp_loc = "%s/%s/tmp" % (settings.MEDIA_ROOT + "/products", owner_slug)
    print("temp_loc : %s" % temp_loc)
    if not os.path.exists(temp_loc):
        os.makedirs(temp_loc)
    temp_file_path = os.path.join(temp_loc, filename)
    if os.path.exists(temp_file_path):
        temp_path = os.path.join(temp_loc, "%s" % (random.random()))
        os.makedirs(temp_path)
        temp_file_path = os.path.join(temp_path, filename)

    temp_image = open(temp_file_path, "wb")
    thumb.save(temp_image, "JPEG")
    print("thumb : %s" % thumb)
    thumb_data = open(temp_file_path, "rb")
    thumb_file = File(thumb_data)
    print("thumb_file : %s" % thumb_file)
    instance.media.save(filename, thumb_file)
    shutil.rmtree(temp_loc, ignore_errors=True)
    return True


#  Aşağıdaki algoritma en boy oranının çok orantısız olduğu durumlarda resmi kırpıyor ve tamamının
#  gözükmesine olanak vermiyor.
def auto_resize_and_crop_image(width, height, max_width, max_height, thumb):
    width_ratio = max_width / width
    height_ratio = max_height / height
    resizing_factor = width_ratio / height_ratio
    if __name__ == '__main__':
        if resizing_factor > 1:  # boy eşit olana kadar resize et yani küçült yada büyüt yani heigth_ratio ile çarp
            resize_ratio = width_ratio
            new_width = int(width * resize_ratio)
            new_heigth = int(height * resize_ratio)
            new_size = (new_width, new_heigth)
            thumb = thumb.resize(new_size, Image.ANTIALIAS)
            crop_size = (new_heigth - max_height) / 2
            left = 0
            top = crop_size
            width = left + max_width
            height = top + max_height
            box = (left, top, width, height)
            thumb = thumb.crop(box)
            return thumb

        else:
            resize_ratio = height_ratio  # eşitse ikisinden biri kadar büyütmek yeterli
            new_width = int(width * resize_ratio)
            new_heigth = int(height * resize_ratio)
            new_size = (new_width, new_heigth)
            thumb = thumb.resize(new_size, Image.ANTIALIAS)
            crop_size = (new_width-max_width) / 2
            left = crop_size
            top = 0
            width = left + max_width
            height = top + max_height
            box = (left, top, width, height)
            thumb = thumb.crop(box)
            return thumb


# Bir de crop'suz algoritma yazabilirim, bu algoritma resmi her zaman kare olacak şekle resize eder.
# Yani olması gereken aspecte resize etmek lazım. O zaman da arka planda beyaz bir resim açıp o resme
# yapıştırmak lazım
def auto_resize_without_crop(width, height, max_width, max_height, thumb):
    max_size_aspect = max_width / max_height
    thumb_aspect = width / height

    if thumb_aspect > max_size_aspect:  # Resmi boydan uzatmak lazım
        new_height = (width / max_size_aspect)
        new_height = math.floor(new_height)
        new_size = (width, new_height)
        new_container_image = Image.new("RGB", new_size, "white")
        left = 0
        top = math.floor((new_height-height)/2)
        box = (left, top)
        new_container_image.paste(thumb, box)
        thumb = new_container_image.resize((max_width, max_height), Image.ANTIALIAS)
        return thumb
    else:
        new_width = math.floor(height * max_size_aspect)
        new_size = (new_width, height)
        new_container_image = Image.new("RGB", new_size, "white")
        left = math.floor((new_width-width)/2)
        top = 0
        box = (left, top)
        new_container_image.paste(thumb, box)
        thumb = new_container_image.resize((max_width, max_height), Image.ANTIALIAS)
        return thumb



