
from django.core.management.base import BaseCommand, CommandError
from products.models import Product

# TODO: ATTENTION ! Please do not run this more than once:
class Command(BaseCommand):
    help = 'Set orders of product images according to their id if order is -1'

    def handle(self, *args, **options):
        all_products = Product.objects.all()[:10]

        for product in all_products:
            self.stdout.write(product.title + " started")
            product_images = product.images.all().order_by("pk")
            if product_images.count() > 0:
                for index, image in enumerate(product_images):
                    self.stdout.write(str(image.pk) + " order : " + str(index))
                    if image.order == -1:
                        image.order = index
                        image.save()
                    # self.stdout.write('product_images_ids for product % : %', product.title, product_images_ids)
            self.stdout.write(product.title + " ended")
        self.stdout.write("product_images_ids ordering finished")
