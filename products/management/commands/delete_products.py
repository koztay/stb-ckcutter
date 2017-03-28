from django.core.management.base import BaseCommand, CommandError
from products.models import Product


class Command(BaseCommand):
    help = 'Deletes all products from db'

    def handle(self, *args, **options):
        all_products = Product.objects.all()

        for product in all_products:
            product_title = product.title
            product.delete()
            self.stdout.write('Successfully deleted %s' % product_title)

        self.stdout.write('Successfully deleted all products')
