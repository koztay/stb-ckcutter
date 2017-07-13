import math

import urllib3
from django.conf import settings
from django.core.files import File
import os
import shutil
from PIL import Image, ImageOps
import random


def download_and_create_new_media_path_for_remote_images(media_path):
    """
    This function downloads images for given media path.
    :param media_path: the path for the media which has to be downloaded
    :return: download path for the image in order to create the thumbnail
    """
    print("I will download the file and use it as local")
    temporary_download_location = settings.STATIC_ROOT + "/tmp/"
    filename = media_path.split("/")[-1]
    temporary_download_path = temporary_download_location + filename
    print(temporary_download_path)

    # create tmp directory if not exists
    if not os.path.exists(temporary_download_location):
        print("path mevcut değil yaratılacak")
        os.makedirs(temporary_download_location)
    else:
        print("path mevcut yaratılmayacak")
    print("media path => ", media_path)
    # if not os.path.exists(temporary_download_path):  # eğer file indirilmemişse indir.
    # print("dosya mevcut değil indirilecek")
    # download the file
    http = urllib3.PoolManager()
    urllib3.disable_warnings()
    with http.request('GET', media_path, preload_content=False) as resp, open(temporary_download_path, 'wb') as out_file:
        if resp.status is 200:
            print("File has been downloaded")
            shutil.copyfileobj(resp, out_file)
        else:
            print("File cannot be downloaded")
            temporary_download_path = ""
            # raise ValueError('A very specific bad thing happened. Response code was not 200')
    print("temporary_download_path :", temporary_download_path)
    return temporary_download_path


def create_new_thumb(media_path, instance, owner_slug, max_width, max_height):
    print("instance at the beginning =>", instance)
    """
    This function creates the thumbnails for image media_path passed from create_new_thumb() fucntion.
    :param media_path: this path is the media path for the image. But I am not sure how this function does not work
    if the download images is false in the task???
    :param instance: this is the instance of the product which image has to be downloaded for.
    :param owner_slug: this is the product slug which is used for creating media
    :param max_width: max_width of the image, the image has been post processed for keeping the dimensions as this
    :param max_height: max_height of the image, the image has been post processed for keeping the dimensions as this
    :return: always True (why???) and creates the thumbnail images with its autoresize function.
    """

    def paste_to_background(image, size):
        """
        This function pastes the image into white background specified in the size parameter.
        :param image: The image to be pasted into background
        :param size: The background size
        :return: the pasted image combined with the background image
        """
        background = Image.new('RGBA', size, (255, 255, 255, 0))
        background.paste(
            image, (int((size[0] - image.size[0]) / 2), int((size[1] - image.size[1]) / 2))
        )
        return background

    if media_path.startswith("http"):
        media_path = download_and_create_new_media_path_for_remote_images(media_path)
    else:
        print("no download necessary")

    print("mediapath_after", media_path)
    if len(media_path) > 0:
        filename = os.path.basename(media_path)
        filename = str(max_width) + "x" + str(max_height) + "-" + filename  # hep aynı isimde yazıyor yoksa
        print("filename : %s" % filename)
        thumb = Image.open(media_path)  # burada patlıyor...
        # width, height = thumb.size mevcut size bilgisine gerek kalmadı...

        """
        thumb = ImageOps.fit(image, size, Image.ANTIALIAS) bu yeni fonksiyonu deneiyoruz...
        """
        # method 1 (crops to fit):
        # desired_size = (max_width, max_height)
        # thumb = ImageOps.fit(thumb, desired_size, Image.ANTIALIAS)

        # method 2 (thumbnail methodu)
        desired_size = max_width, max_height
        thumb.thumbnail(desired_size, Image.ANTIALIAS)

        bg_size = (max_width, max_height)

        thumb = paste_to_background(thumb, bg_size)
        # eski fonksiyon
        # thumb = auto_resize_without_crop(width, height, max_width, max_height, thumb)

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
        print("instance :", instance)
        print("type of instance:", type(instance))
        instance.media.save(filename, thumb_file)
        shutil.rmtree(temp_loc, ignore_errors=True)
    else:
        print("media could not be saved to local, quitting !!!")
    return True
