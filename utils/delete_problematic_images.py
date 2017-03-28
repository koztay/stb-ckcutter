from products.models import ProductImage, Thumbnail


def delete_all():
    thumb_images = Thumbnail.objects.all()
    images_with_problem = [image for image in thumb_images if not image.main_image.get_image_path()]
    delete_problematic(images_with_problem)

    thumb_images_has_no_width = Thumbnail.objects.filter(width=None)
    print("thumb_images has no width", thumb_images_has_no_width)
    delete_problematic(thumb_images_has_no_width)

    all_product_images = ProductImage.objects.all()
    images_with_problem = [image for image in all_product_images if not image.get_image_path()]
    delete_problematic(images_with_problem)

    images_with_problem = [image for image in all_product_images if not image.thumnail_set.all()]
    delete_problematic(images_with_problem)


def delete_problematic(images_with_problem):
    number_of_problematic = len(images_with_problem)
    [image.delete() for image in images_with_problem]
    print("%s problemli resim silindi!" % number_of_problematic)
