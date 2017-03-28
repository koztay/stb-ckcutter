from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from uuslug import slugify

from products.models import (Variation,
                             AttributeType,
                             AttributeValue,
                             Product,
                             Category,
                             Currency,
                             Thumbnail,
                             ProductImage)
from utils import thumbnail_creator


# TODO: bu signal içerisinde kar marjı varsa price 'ı update et, yoksa, kar marjını bulup kaydet.
def product_post_save_receiver_for_variation(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.title = "Default"
        new_var.price = product.price
        # new_var.buying_curreny = Currency.objects.get(name="TURK LIRASI") buna gerek yok.
        new_var.save()


# This receiver function creates predefined product attributes for saved product
def product_post_save_receiver_for_attributes(sender, instance, *args, **kwargs):
    # print("sender:", sender)
    try:
        valueset = instance.valueset
    except:
        valueset = "Error"

    print("valueset:", valueset)
    create_featureset(instance=instance, valueset=valueset)  # buna valueset 'i nasıl göndereceğiz.?


# aşağıdaki fonksiyon çalışıyor aslında iki kez çalışacak bu önce product'ı get_or_create yapacak,
# create yaptığında çalışıp emty value olarak yaratacak, sonra biz bir daha valuset ile birlikte
# çağıracağız.
def create_featureset(instance=None, valueset=None):  # instance içerisinde valuset var ama sıkıntı yaratıyor.

    def get_cell_for_field(field_name):
        importer_map = instance.importer_map
        try:
            field_object = importer_map.fields_set.get(product_field=field_name)
            cell_value_index = int(field_object.get_xml_field())
            cell_value = instance.valueset[cell_value_index]
        except:
            cell_value = ""
        return cell_value

    # featureları al
    product_features = AttributeType.objects.filter(product_type=instance.product_type)
    # eklenenleri al
    assigned_product_features = AttributeType.objects.filter(product=instance)
    # aradaki farka bak : product feature olarak eklenmemiş feature var mı?
    difference = list(set(product_features) - set(assigned_product_features))
    print(len(difference))
    # eğer varsa:
    if len(difference) > 0:  # ilkinde eklenmişse sonradan valuseti nasıl ekleyeceğiz.? Update edeceğiz.
        for feature in difference:  # burada sadece 1 feature varsa sıkıntı olabilir, non iterable diyordu sanki
            feature.product.add(instance)
            feature.save()
            # sonrasında da boş değer yaratıyoruz. Aslında burada import ederken value olacak
            # o yüzden value empty olmayabilir.
            if valueset is not "Error":
                # 1-) get value for the feature
                print("get_cell_for_field :",get_cell_for_field(feature))
                feature_value = get_cell_for_field(feature)

                # 2-) create or update Value for the feature
                attribute_value, attr_created = AttributeValue.objects.get_or_create(attribute_type=feature,
                                                                                     product=instance)
                attribute_value.value = feature_value
                attribute_value.save()
            else:
                AttributeValue.objects.create(attribute_type=feature, product=instance, value="")
    else:  # eklenmemiş ürün feature'ı yok o zaman update et
        if valueset is not "Error":
            for feature in assigned_product_features:
                print("values will be updated for feature:", feature)
                feature_value = get_cell_for_field(feature)
                # update values
                attribute_value, attr_created = AttributeValue.objects.get_or_create(attribute_type=feature,
                                                                                     product=instance)
                attribute_value.value = feature_value
                attribute_value.save()


# This receiver function creates attribute types for existing products after an attribute created
def attribute_type_post_save_receiver(sender, instance, *args, **kwargs):
    # 1 - tüm productlar içerisinde product_type 'ı yeni yaratılan attibute'un product_type'ı aynı olanları süz.
    products = Product.objects.filter(product_type=instance.product_type)
    print(products)
    # 2 - süzülen productlara yeni attribute' u ekle:
    for product in products:
        print(instance)
        assigned_product_features = AttributeType.objects.filter(product=product)
        print("assigned product features :%s" % assigned_product_features)
        if instance not in assigned_product_features:
            instance.product.add(product)
            AttributeValue.objects.create(attribute_type=instance, product=product, value="")


def create_slug(instance, sender, new_slug=None):
    print(instance)
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = sender.objects.filter(slug=slug)
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, sender=sender, new_slug=new_slug)
    return slug


def productimage_post_save_receiver_for_thumbnail(sender, instance, created, *args, **kwargs):
    print('sender : ', sender)
    print('instance', instance)
    print('instance.product', instance.product)

    if sender and instance.image:  # image downloader ile create ediince henüz image set edilmemiş oluyor.
        hd, hd_created = Thumbnail.objects.get_or_create(product=instance.product,
                                                         main_image=instance,
                                                         type='hd')
        sd, sd_created = Thumbnail.objects.get_or_create(product=instance.product,
                                                         main_image=instance,
                                                         type='sd')
        mid, mid_created = Thumbnail.objects.get_or_create(product=instance.product,
                                                           main_image=instance,
                                                           type='medium')
        micro, micro_created = Thumbnail.objects.get_or_create(product=instance.product,
                                                               main_image=instance,
                                                               type='micro')

        # hd_max = (width, height)
        hd_max = (900, 1024)
        sd_max = (500, 600)
        mid_max = (250, 300)
        micro_max = (150, 150)

        media_path = instance.get_image_path()
        print('mediapath nedir?: ', media_path)
        owner_slug = instance.product.slug
        print('owner slug nedir?: ', owner_slug)

        if hd_created:
            thumbnail_creator.create_new_thumb(media_path, hd, owner_slug, hd_max[0], hd_max[1])

        if sd_created:
            thumbnail_creator.create_new_thumb(media_path, sd, owner_slug, sd_max[0], sd_max[1])

        if mid_created:
            thumbnail_creator.create_new_thumb(media_path, mid, owner_slug, mid_max[0], mid_max[1])

        if micro_created:
            thumbnail_creator.create_new_thumb(media_path, micro, owner_slug, micro_max[0], micro_max[1])

        # yukarıdaki gibi if 'ler olduğunda sadece ilk resme ilişkin thumnail yaratıyor. Biz tamamı,
        # için thumbnail yaratmak istiyoruz. Ama bu sefer de thumb resme ait mi değil mi bulmamız gerek.

        # thumbnail_creator.create_new_thumb(media_path, hd, owner_slug, hd_max[0], hd_max[1])
        # thumbnail_creator.create_new_thumb(media_path, sd, owner_slug, sd_max[0], sd_max[1])
        # thumbnail_creator.create_new_thumb(media_path, mid, owner_slug, mid_max[0], mid_max[1])
        # thumbnail_creator.create_new_thumb(media_path, micro, owner_slug, micro_max[0], micro_max[1])

post_save.connect(productimage_post_save_receiver_for_thumbnail, sender=ProductImage)
post_save.connect(product_post_save_receiver_for_attributes, sender=Product)
post_save.connect(product_post_save_receiver_for_variation, sender=Product)
post_save.connect(attribute_type_post_save_receiver, sender=AttributeType)


# TODO : Bunu normal olarak product ve kategori post save olarak yaratamaz mıyız? (mixin vb. yöntemle)
@receiver(pre_save)  # tüm objeler pre_save olmadan çalışıyor...
def slug_pre_save_receiver(sender, instance, *args, **kwargs):
    # print("pre_save_receiver_çalıştı...")

    list_of_models = ('Product', 'Category')
    # print("sender:", sender.__name__)

    if sender.__name__ in list_of_models:  # this is the dynamic part you want
        if not instance.slug:
            instance.slug = create_slug(instance, sender)
    else:
        pass
        # print("sender list of models içinde değil")


#     if sender.__name__ == 'Category':
#         instance.order = instance.id


# @receiver(post_save, sender=Category)
# def category_order_receiver(sender, instance, *args, **kwargs):
#     print("post save category çalışıyor mu?")
#     instance.order = instance.id
#     # instance.save() # bu satır patlatıyor...



