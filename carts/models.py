from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete

from products.models import Variation


# Create your models here.


class CartItem(models.Model):
    cart = models.ForeignKey("Cart")
    item = models.ForeignKey(Variation)
    quantity = models.PositiveIntegerField(default=1)
    line_item_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return "Ürün Kodu: " + self.item.product.istebu_product_no

    def remove(self):
        return self.item.remove_from_cart()

    @property
    def cart_item(self):
        return self.item.title, self.item.quantity

    class Meta:
        ordering = ("item__product__product_type__name", )


def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    # print("cart_item_pre_save_receiver çalıştı")
    qty = instance.quantity
    if int(qty) >= 1:
        price = instance.item.get_sale_price()
        # print("price : ", price)
        line_item_total = Decimal(qty) * Decimal(price)
        instance.line_item_total = line_item_total


pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)


def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
    # print("cart_item_post_save_receiver çalıştı")
    # print("instance var mı:", instance)
    instance.cart.update_subtotal()


post_save.connect(cart_item_post_save_receiver, sender=CartItem)

post_delete.connect(cart_item_post_save_receiver, sender=CartItem)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    items = models.ManyToManyField(Variation, through=CartItem)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    subtotal = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
    tax_percentage = models.DecimalField(max_digits=10, decimal_places=5, default=0.085)
    tax_total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
    total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)

    # discounts
    # shipping

    def __str__(self):
        return str(self.id)

    def update_subtotal(self):
        # print("updating...")
        subtotal = 0
        items = self.cartitem_set.all()
        for item in items:
            subtotal += item.line_item_total
        self.subtotal = "%.2f" % subtotal
        self.save()


def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
    # print("cart presave çalıştı, pre save'de do_tax_and_total_receiver yapıyoruz")
    subtotal = Decimal(instance.subtotal)
    tax_total = round(subtotal * Decimal(instance.tax_percentage), 2)  # 8.5%
    # print(instance.tax_percentage)
    total = round(subtotal + Decimal(tax_total), 2)
    instance.tax_total = "%.2f" % tax_total
    instance.total = "%.2f" % total


# instance.save()

pre_save.connect(do_tax_and_total_receiver, sender=Cart)
