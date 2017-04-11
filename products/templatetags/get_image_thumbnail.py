from django import template
from ..models import ProductImage, THUMB_CHOICES

register = template.Library()


@register.filter
def get_image_thumbnail(obj, arg):
    """
    obj == ProductImage instance

    """
    print("object_type :", type(obj))
    arg = arg.lower()
    # if not isinstance(obj, ProductImage):
    #     raise TypeError("This is not a valid productimage model.")
    choices = dict(THUMB_CHOICES)
    if not choices.get(arg):
        raise TypeError("This is not a valid type for this model.")
    try:
        return obj.thumbnail_set.filter(type=arg).first().media.url
    except:
        return None
