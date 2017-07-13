from django.conf import settings
from django.core.management.base import BaseCommand
from products.models import Product, Thumbnail
from utils import thumbnail_creator

hd_max = settings.HD_MAX
sd_max = settings.SD_MAX
mid_max = settings.MEDIUM_MAX  # bunu yatayda 350 pixelin altına ayarlayınca zoom lens sapıtıyor.
micro_max = settings.MICRO_MAX

"""
Bu komut düzgün çalışmıyor. Örneğin eksik thumbnailleri indiremiyor.
Ancak eğer resmin orijinali indirilrken hata olmuşsa (bazan şeffaf 30x30 ikon benzeri bir resim olarak
kaydediyor neden bilmiyorum ama oluyor.
Netice itibarıyla resimlerin orijinali bozuksa bu komut tespit edip silmemizi sağlıyor.
Akabinde bozuk resimler silindikten sonra eğer eksik thumb varsa o zaman

for image in images:
    image.save()
    
ile tüm eksik thumbnailler tamamlanıyor.

"""

class Command(BaseCommand):
    create_micro = False
    create_medium = False
    create_sd = False
    create_hd = False
    _micro = False
    _medium = False
    _sd = False
    _hd = False

    micro_instance = None
    medium_instance = None
    sd_instance = None
    hd_instance = None

    def add_arguments(self, parser):
        # # Positional arguments
        parser.add_argument('thumb_type', nargs='+', type=str)

        # Named (optional) arguments
        # parser.add_argument(
        #     '--delete',
        #     action='store_true',
        #     dest='delete',
        #     default=False,
        #     help='Delete poll instead of closing it',
        # )

    help = 'Downloads missing thumbnails for products'

    def handle(self, *args, **options):
        thumb_type = options['thumb_type'][0]

        self.stdout.write("Thumb Type: " + thumb_type)
        self.stdout.write("Type of : " + str(type(thumb_type)))

        if thumb_type == "micro":
            self._micro = True
        elif thumb_type == "medium":
            self._medium = True
        if thumb_type == "sd":
            self._sd = True
        elif thumb_type == "hd":
            self._hd = True

        orphan = Thumbnail.objects.filter(width__isnull=True)
        self.stdout.write(str(orphan.count()) + " adet orphan Thumbnail bulundu...")
        for image in orphan:
            image.delete()

        all_products = Product.objects.all().order_by("title")

        for product in all_products:
            product_images = product.images.all()
            if product_images.count() > 0:
                for product_image in product_images:

                    try:
                        self.micro_instance = product_image.micro_thumb  # burada instance yok, instance'a ait url var!
                        print(self.micro_instance)
                        if "Image has no" in self.micro_instance:
                            print("Image has no var diyor ama http:// var")
                            self.stdout.write("micro exists!!!! => do not create micro thumb in db, but download image")
                            if self._micro is True:
                                self.create_micro = True
                                self.micro_instance, created = Thumbnail.objects.get_or_create(product=product,
                                                                                               main_image=product_image,
                                                                                               type='micro')

                    except:
                        self.stdout.write("micro does not existss => " + str(product_image.pk) + " " + product.title)



                    try:
                        self.medium_instance = product_image.medium_thumb
                        if "Image has no" in self.medium_instance:
                            self.stdout.write("medium does not exist!!!! => create medium thumb")
                    except:
                        self.stdout.write("medium sıçtı => " + str(product_image.pk) + " " + product.title)
                        if self._medium is True:
                            self.stdout.write("medium is true")
                            self.create_medium = True
                    try:
                        self.sd_instance = product_image.sd_thumb
                        if "Image has no" in self.sd_instance:
                            self.stdout.write("sd does not exist!!!! => create sd thumb")
                    except:
                        self.stdout.write("sd sıçtı => " + str(product_image.pk) + " " + product.title)
                        if self._sd is True:
                            self.stdout.write("sd is true")
                            self.create_sd = True

                    try:
                        self.hd_instance = product_image.hd_thumb
                        if "Image has no" in self.hd_instance:
                            self.stdout.write("hd does not exist!!!! => create hd thumb")
                    except:
                        self.stdout.write("hd sıçtı => " + str(product_image.pk) + " " + product.title)
                        if self._hd is True:
                            self.stdout.write("hd is true")
                            self.create_hd = True

                    media_path = product_image.get_image_path()
                    # print('mediapath nedir?: ', media_path)
                    owner_slug = product.slug
                    # print('owner slug nedir?: ', owner_slug)

                    if self.create_micro is True and not type(self.micro_instance) == str:
                        print(self.create_micro)
                        print(self.micro_instance)
                        print("bunlarla create başlattım")

                        thumbnail_creator.create_new_thumb(media_path, self.micro_instance, owner_slug, micro_max[0],
                                                           micro_max[1])

                    if self.create_medium is True and not type(self.medium_instance) == str:
                        thumbnail_creator.create_new_thumb(media_path, self.medium_instance, owner_slug, mid_max[0],
                                                           mid_max[1])

                    if self.create_sd is True and not type(self.sd_instance) == str:
                        thumbnail_creator.create_new_thumb(media_path, self.sd_instance, owner_slug, sd_max[0],
                                                           sd_max[1])

                    if self.create_hd is True and not type(self.hd_instance) == str:
                        thumbnail_creator.create_new_thumb(media_path, self.hd_instance, owner_slug, hd_max[0],
                                                           hd_max[1])


        self.stdout.write("product_image thumb check finished")
