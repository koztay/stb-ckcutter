from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Case, Count, F, Max, Q, Value, When
from django.utils.safestring import mark_safe

# third party apps
from multiselectfield import MultiSelectField
from uuslug import slugify
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField


# for Thumbnail Class
def thumbnail_location(instance, filename):
    return "products/%s/thumbnails/%s" % (instance.product.slug, filename)

THUMB_CHOICES = (
    ("hd", "HD"),
    ("sd", "SD"),
    ("medium", "Medium"),
    ("micro", "Micro"),
)


# For ProductImage Class
# This utility function creates the filename and filepath according to the slug and product instance
def image_upload_to(instance, filename):
    title = instance.product.title
    if len(title) > 50:
        title = title[:50]
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "products/%s/%s" % (slug, new_filename)


# This utility function creates the filename and filepath according to the slug and product instance
def image_upload_to_featured(instance, filename):
    title = instance.product.title
    if len(title) > 50:
        title = title[:50]
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "products/%s/featured/%s" % (slug, new_filename)
# ************************************************************************************************************ #


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset().active()

    def get_related(self, instance):
        products_one = self.get_queryset().filter(categories__in=instance.categories.all()).filter(variation__inventory__gte=0)
        products_two = self.get_queryset().filter(default=instance.default).filter(variation__inventory__gte=0)
        qs = (products_one | products_two).exclude(id=instance.id).distinct()
        return qs


class Product(models.Model):

    FRONT_PAGE_TABS = (
        ("OC", "ÖNE ÇIKANLAR"),
        ("FU", "FIRSAT ÜRÜNLERİ"),
        ("KU", "KAMPANYALI ÜRÜNLER"),
        ("CS", "ÇOK SATANLAR"),
        ("GT", "GÜNÜN TEKLİFLERİ"),
        ("HT", "HAFTANIN ÜRÜNLERİ"),
        ("DU", "DİĞER ÜRÜNLER")  # TODO : ARADIKLARINIZA BENZER ÜRÜNLER ALGORİTMASI YAZ
    )

    """
    Günün Teklifleri
*Haftanın ürünleri
*Aradıklarınıza Benzer Ürünler (Aradıkları ürün gruplarından ürünleri gösterebilirsek bu olsun)
*İlginizi Çekebilecek Diğer Ürünler (Bir üstteki olmazsa bu olsun)
    """

    title = models.CharField(db_index=True, max_length=1000)
    # description = models.TextField(blank=True, null=True)
    sub_title = models.CharField(max_length=1000, blank=True, null=True)  # n11 ve gg için alt başlık değeri
    description = RichTextField(db_index=True, default="<h1>default description</h1>", blank=True, null=True)
    price = models.DecimalField(db_index=True, decimal_places=2, max_digits=20, blank=True, null=True)
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField('Category', blank=True)
    product_type = models.ForeignKey('ProductType', null=True, blank=True)
    # attribute_type = models.ManyToManyField('AttributeType')
    default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True)
    # yukarıdaki default field 'ı related products için gerekli. Algoritmayı incelemedim ama daha
    # iyi bir yol bulunabilir. // TODO: Bu field 'a gerek olmayacak şekilde düzenleme yap.
    slug = models.SlugField(blank=True, unique=True, max_length=1000)  # unique=True)
    frontpage_grup = MultiSelectField(choices=FRONT_PAGE_TABS, null=True, blank=True)
    show_on_homepage = models.BooleanField(default=True)
    show_on_popular = models.BooleanField(default=True)

    tags = TaggableManager(blank=True)
    # taggable manager ile ilgili bir hata veriyor test edilemiyor.

    kdv = models.FloatField(default=18.0)
    desi = models.IntegerField(default=1)
    kargo = models.CharField(max_length=50, null=True, blank=True)  # kargo ücretini kimin ödediği bilgisi
    kargo_suresi = models.CharField(max_length=50, null=True, blank=True)  # kaç günde kargolandığı bilgisi

    istebu_product_no = models.CharField(max_length=100, null=True, blank=True)
    vendor_product_no = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        ordering = ["-variation__inventory", "id", "title", ]

    def __str__(self):  # def __str__(self):
        return self.title

    def get_brand(self):
        attr_type = AttributeType.objects.filter(type="Marka")
        attr = AttributeValue.objects.filter(attribute_type=attr_type, product=self)
        # print("attr : ", attr)
        marka = "No Brand Set for Product"
        for attribute in attr:
            # print(attribute)
            if attribute.value:
                # print("marka niye yazmaz baba :", attribute.value)
                marka = attribute.value
        return marka

    def get_absolute_url(self):
        view_name = "products:product_detail"
        # view_name = "products:product_detail_slug_function"
        return reverse(view_name, kwargs={"slug": self.slug})

    def get_main_category(self):  # bu quickview 'da ürününü kategorisini göstermek için...
        categories = Category.objects.all().filter(product=self)
        for category in categories:
            if category.is_child:
                pass
            else:
                return category

    def get_total_views(self):
        number_of_views = 0
        views = self.productview_set.all()
        for view in views:
            number_of_views += view.count
        print(number_of_views)
        return number_of_views

    # Bu metodu sol üst köşedeki cart list içerisindeki imajı set etmek için kullanıyoruz.
    # O nedenle bu metodu silme. Diğerlerini silmek için şimdilik bir sakınca görünmüyor.
    @property
    def micro_thumb(self):
        first_image = ProductImage.objects.all().filter(product=self).first()
        micro_thumb = Thumbnail.objects.all().filter(main_image=first_image, type='micro').first()
        # print(micro_thumb.media.url)
        return micro_thumb.media.url

# ************************************************************************************************************ #


class Currency(models.Model):
    NAME_CHOICES = (
        ("TL", "TURK LIRASI"),
        ("USD", "AMERIKAN DOLARI"),
        ("EUR", "EURO"),
    )
    name = models.CharField(max_length=10, choices=NAME_CHOICES, unique=True, default='TL')
    updated = models.DateField(auto_now=True)
    value = models.FloatField(default=1.0)

    class Meta:
        verbose_name = 'currency'
        verbose_name_plural = 'currencies'

    def __str__(self):
        return self.name


# ************************************************************************************************************ #

# delete this model and use product instead of this like commenting system. So, products belongs
# products like comments. And if product has child products we use an algorithm which one to show.
"""

class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset().active()

    def get_related(self, instance):
        products_one = self.get_queryset().filter(categories__in=instance.categories.all()).filter(variation__inventory__gte=0)
        products_two = self.get_queryset().filter(default=instance.default).filter(variation__inventory__gte=0)
        qs = (products_one | products_two).exclude(id=instance.id).distinct()
        return qs


"""


class VariationQueryset(models.query.QuerySet):
    def active(self):
        return self.filter(product__active=True)

    def local_price(self):
        qs = self.active()
        local_field = F("sale_price")*F("buying_currency__value")
        local_field.output_field = models.DecimalField()
        return qs.annotate(local_price=local_field)

    # def all(self):
    #     return self.local_price()


class Variation(models.Model):

    """
    Bu sınıfı vendorlar Penta, Arena vb. XML çekmek için için silmeyeceğiz. Farklı her vendor
    için bir variation yaratacağız. Dolayısıyla bir ürünü 5 farklı yerden alıyorsak 5 farklı
    variation olacak. Variation 'ları product 'lara bağlarken tıpkı bizim eski sistemdeki gibi
    havuz benzeri bir yere toplamak ve sonrasında ürünü edit edip bir product'a bağlamak gerek.
    Eğer ilişkili bir product yoksa da o zaman bu variantı product'a çevir demek gerek.
    Tüm bunları yok edip variation modeli silsek, product altında product oluşsa comment sistemi gibi.
    Daha mantıklı olmaz mı?
    Belki bunu manage.py ile kendi komutumuzu oluşturarak yapabiliriz, ya da admin panelden belki olur.
    Ancak burada sitede hangi vendora ait variationı göstereceğimize karar
    verecek bir algoritma olmalı. Add to cart yaptığımızda otomatik olarak algoritmaya
    göre hangi variation eklenecekse onun eklenmesi lazım. Kullanıcı variation seçememeli,
    ama ürün tipi seçebilmeli, yani size, color vb. gibi ürün tipi.
    """
    active = models.BooleanField(default=False)  # import nedeniyle manual active edilecek.
    product = models.ForeignKey(Product, null=True, blank=True)
    # import ederken hangi producta bağlanacak belli değil o yüzden yukarıdaki foreignkey kısmında null ve blank True.
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    buying_currency = models.ForeignKey(Currency, null=True, blank=True)  # null means TL
    buying_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    gittigidiyor_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    n11_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    inventory = models.IntegerField(null=True, blank=True)  # refer none == unlimited amount
    product_barkod = models.CharField(max_length=100, null=True, blank=True)
    # vendor = models.ForeignKey('vendors.Vendor', null=True, blank=True)
    # vendor_product_no = models.CharField(max_length=100, null=True, blank=True)
    # product alanı içerisinde de vendor_product_no var. XML çekerken, XML 'e de vendoru eklemek lazım. Dolayısıyla,
    # her xml kendine ait olan variationa yazar buying price ve buying currency değerlerini. Sitede göstermek için de
    # product sayfasında hangi vendor seçiliyse onun ürünü gösterilir. Eşleştirirken de önce vendoru kendi olan ürünleri
    # bulur sonra kendine ait vendor no.lu ürün var mı bakar varsa update eder yoksa pas geçer. Şimdilik yukarıdaki
    # modelleri eklemeyeyim.
    objects = models.Manager()
    annotated = VariationQueryset.as_manager()
    # objects = VariationQueryset.as_manager()

    def __str__(self):
        return self.title

    # eğer ürünü import ederek eklemişsek variation'ın hem price hem de sale price kısmı empty geliyordu.
    # aşağıdaki revizyon ile düzelttim bakalım düzgün çalışacak mı?
    # "{:,.2f}".format(self.sale_price * Decimal(self.buying_currency.value))
    # "{:,.2f}".format(value) => thousands seperator işlevi sağlıyor, ancak sepete eklerken bu sorun yaratıyor...

    def get_xml_sale_price(self, market):
        if market == "gittigidiyor":
            if self.gittigidiyor_price is not None:
                return "{:.2f}".format(self.gittigidiyor_price * Decimal(self.buying_currency.value))
        elif market == "n11":
            if self.n11_price is not None:
                return "{:.2f}".format(self.n11_price * Decimal(self.buying_currency.value))
        return self.get_sale_price()

    def get_sale_price(self):
        if self.sale_price is not None:
            return "{:.2f}".format(self.sale_price * Decimal(self.buying_currency.value))
        elif self.price is not None:
            return "{:.2f}".format(self.price * Decimal(self.buying_currency.value))
        else:
            return "{:.2f}".format(self.get_product_price())

    def get_product_price(self):
        if self.product.price:
            return "{:.2f}".format(self.product.price * Decimal(self.buying_currency.value))
        else:
            return 0

    def get_html_price(self):
        if self.sale_price is not None:
            if float(self.get_sale_price()) < float(self.get_product_price()):
                html_text = '<span class="aa-product-price">%s ,-₺</span> <span class="aa-product-price"><del>%s ,-₺</del></span>' % ("{:,.2f}".format(float(self.get_sale_price())), "{:,.2f}".format(float(self.get_product_price())))
            else:
                html_text = "<span class='aa-product-price'>%s ,-₺</span>" % "{:,.2f}".format(float(self.get_sale_price()))
        else:
            html_text = "<span class='aa-product-price'>%s ,-₺</span>" % "{:,.2f}".format(float(self.get_product_price()))
        return mark_safe(html_text)

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def add_to_cart(self):
        return "%s?item=%s&qty=1" % (reverse("cart"), self.id)

    def remove_from_cart(self):
        return "%s?item=%s&qty=1&delete=True" % (reverse("cart"), self.id)
        # return "%s?item=%s&qty=0" % (reverse("cart"), self.id)

    def get_title(self):
        if self.title == "Default":
            return "%s" % self.product.title
        else:
            return "%s - %s" % (self.product.title, self.title)

# ************************************************************************************************************ #


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images')
    image = models.ImageField(upload_to=image_upload_to, blank=True, null=True, max_length=1000)
    remote_url = models.URLField(blank=True, null=True)

    def get_image_path(self):
        # img = self.image
        if self.image and hasattr(self.image, 'url'):
            img_url = self.image.url

            if "http" not in img_url:  # cloud kullanmıyoruz demektir
                print("img_url", img_url)
                # remove MEDIA_URL from img_url
                img_url = img_url.replace(settings.MEDIA_URL, "/", 1)
                # combine with media_root
                img_path = settings.MEDIA_ROOT + img_url
                print("img_path", img_url)
                print("amazon 'da bu ikisi arasındaki fark nasıl acaba?")
                return img_path
            else:
                return img_url
        else:
            return None  # None

    def __str__(self):
        return self.product.title

    # // Aşağıdakiler için parametre olarak 'type' alan tek bir fonksiyon yazaydın ya...
    @property
    def micro_thumb(self):
        micro_thumb = Thumbnail.objects.all().filter(main_image=self, type='micro').first()
        if micro_thumb.media:
            return micro_thumb.media.url
        else:
            return "Image has no Micro Thumbnail"

    @property
    def medium_thumb(self):
        medium_thumb = Thumbnail.objects.all().filter(main_image=self, type='medium').first()
        if medium_thumb.media:
            return medium_thumb.media.url
        else:
            return "Image has no Medium Thumbnail"

    @property
    def sd_thumb(self):
        sd_thumb = Thumbnail.objects.all().filter(main_image=self, type='sd').first()

        # print("sd_thumb var mı?", sd_thumb, self) # try blocku içine koymazsan error durumunda xml output patlıyor.
        try:
            url = sd_thumb.media
        except:
            url = "Image has no SD Thumbnail"

        return url

    @property
    def hd_thumb(self):
        hd_thumb = Thumbnail.objects.all().filter(main_image=self, type='hd').first()
        if hd_thumb.media:
            return hd_thumb.media.url
        else:
            return "Image has no HD Thumbnail"

# ************************************************************************************************************ #


# aşağıdaki queryseti refactor etmeye başladım, ancak cloud 'a yükleme yapıp test etmeliyim.
class CategoryQueryset(models.query.QuerySet):
    def root_categories(self):  # which has no parent
        return self.filter(parent__isnull=True)

    def child_categories(self):  # they can also be root for another child
        return self.filter(parent__isnull=False)

    # yukarıdaki her iki func da işe yaramaz.
    # def stale(self, cutoff=datetime.timedelta(hours=1)):
    #     end_time = now() - cutoff
    #     return self.annotate(
    #         last_check=Max('checkresult__checked_on')
    #     ).filter(
    #         Q(last_check__lt=end_time) | Q(last_check__isnull=True))


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQueryset(self.model, using=self._db).order_by("title")

    def roots(self):
        return self.get_queryset().root_categories()

    # bunun altını neden çiziyor anlamadım?
    def categories_with_children(self, *args, **kwargs):
        custom_list = [category.id for category in Category.objects.all() if category.get_children() is not None]
        return Category.objects.filter(pk__in=custom_list)  # tekrar queryset döndürdük.


# Product Category
class Category(models.Model):
    parent = models.ForeignKey("self", null=True, blank=True)
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(blank=True, unique=True, max_length=1000)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    show_on_homepage = models.BooleanField(default=True)
    order = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = models.Manager()  # The default manager.
    with_childrens = CategoryManager()

    class Meta:
        ordering = ('title',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("categories:category_detail", kwargs={"slug": self.slug})

    @property
    def is_child(self):
        if self.parent is not None:
            return True
        else:
            return False

    def get_children(self):
        children = Category.objects.filter(parent=self)  # tüm kategoriler içerisinde parenti benim olduklarımı listele
        if len(children) > 0:  # eğer listede eleman varsa bunlar benim children 'ımdır.
            return children
        else:
            return None


# ************************************************************************************************************ #

# Bu ürünleri Justin anasayfada tam ekran resim ise banner gibi gösteriyordu, bizde kullanılmıyor bu model.
class ProductFeatured(models.Model):
    product = models.ForeignKey(ProductImage)
    image = models.ImageField(upload_to=image_upload_to_featured, max_length=2000)
    title = models.CharField(max_length=120, null=True, blank=True)
    text = models.CharField(max_length=220, null=True, blank=True)
    text_right = models.BooleanField(default=False)
    text_css_color = models.CharField(max_length=6, null=True, blank=True)
    show_price = models.BooleanField(default=False)
    make_image_background = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.product.title


# ************************************************************************************************************ #


class ProductType(models.Model):
    name = models.CharField(max_length=120, default="Generic Product")

    def __str__(self):
        return self.name


# ************************************************************************************************************ #


class AttributeType(models.Model):
    product_type = models.ForeignKey(ProductType)
    order = models.IntegerField(default=0)
    product = models.ManyToManyField(Product, blank=True)
    type = models.CharField(max_length=120)

    def __str__(self):
        return self.type


# ************************************************************************************************************ #


class AttributeValue(models.Model):
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=120, default="")

    def __str__(self):
        return self.value

# ************************************************************************************************************ #


class Thumbnail(models.Model):
    product = models.ForeignKey(Product)  # instance.product.title
    main_image = models.ForeignKey(ProductImage)
    type = models.CharField(max_length=20, choices=THUMB_CHOICES, default='hd')
    height = models.CharField(max_length=20, null=True, blank=True)
    width = models.CharField(max_length=20, null=True, blank=True)
    media = models.ImageField(
        width_field="width",
        height_field="height",
        blank=True,
        null=True,
        upload_to=thumbnail_location,
        max_length=2000)

    def __str__(self):  # __str__(self):
        return str(self.product.title + " " + self.type + " thumbnail image for main image with pk :" + str(self.main_image.pk))


# ************************************************************************************************************ #
"""
This way you have a clear picture of how each attribute relates to some vehicle.

Forms

Basically, with this database design, you would require two forms for adding objects into the
database. Specifically a model form for a vehicle and a model formset for attributes.
You could use jQuery to dynamically add more items on the Attribute formset.

Note

You could also separate Attribute class to AttributeType and AttributeValue so you don't have
redundant attribute types stored in your database or if you want to limit the attribute choices
for the user but keep the ability to add more types with Django admin site.

To be totally cool, you could use autocomplete on your form to suggest existing attribute types to the user.

Hint: learn more about database normalization.

"""

"""
class Person(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):              # __unicode__ on Python 2
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through='Membership')

    def __str__(self):              # __unicode__ on Python 2
        return self.name

class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=64)
"""
