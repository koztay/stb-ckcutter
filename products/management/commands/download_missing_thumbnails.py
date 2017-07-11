from django.core.management.base import BaseCommand, CommandError
from products.models import Product


class Command(BaseCommand):
    help = 'Downloads missing thumbnails for products'

    def handle(self, *args, **options):
        all_products = Product.objects.all().order_by("title")

        for product in all_products:
            # self.stdout.write(product.title + " started")
            product_images = product.images.all()
            if product_images.count() > 0:
                for product_image in product_images:
                    try:
                        micro = product_image.micro_thumb
                        if "Image has no" in micro:
                            self.stdout.write("micro does not esixt!!!! => create micro thumb")
                    except:
                        self.stdout.write("micro sıçtı =>" + str(product_image.pk) + " " + product.title)

                    try:
                        medium = product_image.medium_thumb
                        if "Image has no" in medium:
                            self.stdout.write("medium does not esixt!!!! => create medium thumb")
                    except:
                        self.stdout.write("medium sıçtı =>" + str(product_image.pk) + " " + product.title)

                    try:
                        sd = product_image.sd_thumb
                        if "Image has no" in sd:
                            self.stdout.write("sd does not esixt!!!! => create sd thumb")
                    except:
                        self.stdout.write("sd sıçtı =>" + str(product_image.pk) + " " + product.title)

                    try:
                        hd = product_image.hd_thumb
                        if "Image has no" in hd:
                            self.stdout.write("hd does not esixt!!!! => create hd thumb")
                    except:
                        self.stdout.write("hd sıçtı =>" + str(product_image.pk) + " " + product.title)

        self.stdout.write("product_image thumb check finished")
