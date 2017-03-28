from django import template
from ..models import Promotion, THUMB_CHOICES

register = template.Library()


@register.filter
def get_promotion_thumbnail(obj, arg):
    """
    obj == Product instance

    """
    arg = arg.lower()
    if not isinstance(obj, Promotion):
        raise TypeError("This is not a valid product model.")
    choices = dict(THUMB_CHOICES)
    if not choices.get(arg):
        raise TypeError("This is not a valid type for this model.")
    try:
        return obj.promotionthumbnail_set.filter(type=arg).first().media.url
    except:
        return None
