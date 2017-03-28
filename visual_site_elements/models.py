from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.text import slugify
from utils import thumbnail_creator


# Create your models here.
def thumbnail_location(instance, filename):
    return "promotions/%s/thumbnails/%s" % (instance.promotion.slug, filename)

THUMB_CHOICES = (
    ("lg", "Large"),  # 450x450
    ("md", "Medium"),  # 300x220
    ("micro", "Micro"),  # 150x150
)


# This utility function creates the filename and filepath according to the slug and product instance
def image_upload_to(instance, filename):
    title = instance.title
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "site_images/%s/%s" % (slug, new_filename)


class SliderImage(models.Model):
    """
    Bu sınıf anasayfadaki en üstte çıkan en büyük resimlerin olduğu sliderları yönetmek için.
    """
    title = models.CharField(max_length=120)  # bu o slide  için en büyük başlık
    sub_title = models.CharField(max_length=80)  # bu kısa açıklama
    campaign = models.CharField(max_length=120)  # bu da en tepedeki kampanya başlığı
    image = models.ImageField(upload_to=image_upload_to)  # slider size 1920x700 ebatında.
    url = models.CharField(max_length=250)
    active = models.BooleanField(default=True)

    def get_image_path(self): # Buna gerek olmayabilir, çünkü kesme biçme yok, ama ileride
        # onu da yapmak gerekebilir... O nednele şimdilik kalsın...
        # img = self.image

        img_url = self.image.url
        # remove MEDIA_URL from img_url
        img_url = img_url.replace(settings.MEDIA_URL, "/", 1)
        # combine with media_root
        img_path = settings.MEDIA_ROOT + img_url
        if img_url:
            return img_path
        return img_path  # None

    def __str__(self):
        return self.title


class Promotion(models.Model):
    """
    Bu sınıf sliderın altındaki promosyonları yönetmek için. Bu sınıfta birden fazla
    ebatta resim var dolayısıyla bu sınıfın resimlerini product sınıfı içerisinde
    thumbnail yaratan utils.py ile yapmak gerekebilir. Ayrıca utils.py 'ı başka
    yerlerden de kullanacaksam o zaman ayrı bir klasör ile modül olarak ayırmak
    daha doğru olmaz mı?
    """
    title = models.CharField(max_length=120)  # bu o slide  için en büyük başlık
    sub_title = models.CharField(max_length=80)  # bu kısa açıklama
    image = models.ImageField(upload_to=image_upload_to)  # slider size 450x450 ve 300x220 ebatında.
    url = models.CharField(max_length=250)
    slug = models.SlugField(blank=True, )
    active = models.BooleanField(default=True)

    def get_image_path(self):
        # img = self.image

        img_url = self.image.url
        # remove MEDIA_URL from img_url
        img_url = img_url.replace(settings.MEDIA_URL, "/", 1)
        # combine with media_root
        img_path = settings.MEDIA_ROOT + img_url
        if img_url:
            return img_path
        return img_path  # None

    def __str__(self):
        return self.title


class PromotionThumbnail(models.Model):
    promotion = models.ForeignKey(Promotion)  # instance.promotion.title
    type = models.CharField(max_length=20, choices=THUMB_CHOICES, default='lg')
    height = models.CharField(max_length=20, null=True, blank=True)
    width = models.CharField(max_length=20, null=True, blank=True)
    media = models.ImageField(
        width_field="width",
        height_field="height",
        blank=True,
        null=True,
        upload_to=thumbnail_location)

    def __str__(self):  # __str__(self):
        return str(self.media.path)


class HorizontalBanner(models.Model):
    title = models.CharField(max_length=120)  # bu o slide  için en büyük başlık
    image = models.ImageField(upload_to=image_upload_to)  # slider size 1170x170 ebatında.
    url = models.CharField(max_length=250)
    active = models.BooleanField(default=True)

    def __str__(self):  # __str__(self):
        return str(self.title)


class Testimonial(models.Model):
    name_of_person = models.CharField(max_length=120)  # yorumu yapan kişinin adı
    comment = models.TextField()
    comment_date = models.DateField()
    image = models.CharField(max_length=500)  # satın aldığı ürünün resim linki n11 'deki
    url = models.CharField(max_length=250)  # N11 veya gittigidiyordaki sayfa linki
    active = models.BooleanField(default=True)

    def __str__(self):  # __str__(self):
        return str(self.name_of_person)


#  Aşağıdaki signals fonksiyonlarını ayırmaya gerek görmedim...
def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Promotion.objects.filter(slug=slug)
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def promotion_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


def promotion_post_save_receiver_for_thumbnail(sender, instance, created, *args, **kwargs):
    if sender:  # bu ilk seferde neden None döndürüyor anlamadım?
        hd, hd_created = PromotionThumbnail.objects.get_or_create(promotion=instance, type='lg')
        sd, sd_created = PromotionThumbnail.objects.get_or_create(promotion=instance, type='md')
        micro, micro_created = PromotionThumbnail.objects.get_or_create(promotion=instance, type='micro')

        lg_max = (450, 450)
        md_max = (300, 220)
        micro_max = (150, 150)

        media_path = instance.get_image_path()
        owner_slug = instance.slug
        if hd_created:
            thumbnail_creator.create_new_thumb(media_path, hd, owner_slug, lg_max[0], lg_max[1])

        if sd_created:
            thumbnail_creator.create_new_thumb(media_path, sd, owner_slug, md_max[0], md_max[1])

        if micro_created:
            thumbnail_creator.create_new_thumb(media_path, micro, owner_slug, micro_max[0], micro_max[1])


pre_save.connect(promotion_pre_save_receiver, sender=Promotion)
post_save.connect(promotion_post_save_receiver_for_thumbnail, sender=Promotion)
