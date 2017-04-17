from django.contrib import admin
# here below is for Flatpages CKEditor integration
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models

from ckeditor.widgets import CKEditorWidget

from .models import SliderImage, Promotion, PromotionThumbnail, HorizontalBanner, Testimonial, HorizontalTopBanner


# FlatPages CKEditor integration
class FlatPageCustom(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageCustom)


class PromotionThumbnailInline(admin.TabularInline):
    extra = 1
    model = PromotionThumbnail


class PromotionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
        PromotionThumbnailInline,
    ]

    class Meta:
        model = Promotion

admin.site.register(SliderImage)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(HorizontalBanner)
admin.site.register(HorizontalTopBanner)
admin.site.register(Testimonial)
