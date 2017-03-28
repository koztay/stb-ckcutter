from django.contrib import admin
from .models import SliderImage, Promotion, PromotionThumbnail, HorizontalBanner, Testimonial


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
admin.site.register(Testimonial)
