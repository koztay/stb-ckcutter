from django.conf import settings
from django.core.management.base import BaseCommand
from products.models import Product, Thumbnail
from utils import thumbnail_creator

hd_max = settings.HD_MAX
sd_max = settings.SD_MAX
mid_max = settings.MEDIUM_MAX  # bunu yatayda 350 pixelin altına ayarlayınca zoom lens sapıtıyor.
micro_max = settings.MICRO_MAX


class Command(BaseCommand):
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

        _micro = False
        _medium = False
        _sd = False
        _hd = False

        self.stdout.write("Thumb Type: " + thumb_type)
        self.stdout.write("Type of : " + str(type(thumb_type)))

        if thumb_type == "micro":
            _micro = True
        elif thumb_type == "medium":
            _medium = True
        if thumb_type == "sd":
            _sd = True
        elif thumb_type == "hd":
            _hd = True

        orphan = Thumbnail.objects.filter(width__isnull=True)
        self.stdout.write(str(orphan.count()) + " adet orphan Thumbnail bulundu...")
        for image in orphan:
            image.delete()

        all_products = Product.objects.all().order_by("title")

        for product in all_products:
            # self.stdout.write(product.title + " started")
            product_images = product.images.all()
            if product_images.count() > 0:
                for product_image in product_images:
                    try:
                        micro = product_image.micro_thumb
                        if "Image has no" in micro:
                            self.stdout.write("micro does not exist!!!! => create micro thumb")
                            if _micro is True:
                                self.stdout.write("micro is true")
                                micro, micro_created = Thumbnail.objects.get_or_create(product=product,
                                                                                       main_image=product_image,
                                                                                       type='hd')

                                media_path = product_image.get_image_path()
                                print('mediapath nedir?: ', media_path)
                                owner_slug = product.slug
                                print('owner slug nedir?: ', owner_slug)
                                if micro_created:
                                    self.stdout.write("micro_created")
                                    thumbnail_creator.create_new_thumb(media_path, micro, owner_slug, micro_max[0],
                                                                       micro_max[1])
                    except:
                        self.stdout.write("micro sıçtı => " + str(product_image.pk) + " " + product.title)


                    try:
                        medium = product_image.medium_thumb
                        if "Image has no" in medium:
                            self.stdout.write("medium does not exist!!!! => create medium thumb")
                    except:
                        self.stdout.write("medium sıçtı => " + str(product_image.pk) + " " + product.title)
                        if _medium is True:
                            self.stdout.write("medium is true")
                            product_image.save()

                    try:
                        sd = product_image.sd_thumb
                        if "Image has no" in sd:
                            self.stdout.write("sd does not exist!!!! => create sd thumb")
                    except:
                        self.stdout.write("sd sıçtı => " + str(product_image.pk) + " " + product.title)
                        if _sd is True:
                            self.stdout.write("sd is true")
                            product_image.save()

                    try:
                        hd = product_image.hd_thumb
                        if "Image has no" in hd:
                            self.stdout.write("hd does not exist!!!! => create hd thumb")
                    except:
                        self.stdout.write("hd sıçtı => " + str(product_image.pk) + " " + product.title)
                        if _hd is True:
                            self.stdout.write("hd is true")
                            product_image.save()

        self.stdout.write("product_image thumb check finished")
