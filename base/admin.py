from django.contrib import admin
from . import models


class ImageModelInline(admin.TabularInline):
    model = models.ProductImage
    extra = 3


class YourModelAdmin(admin.ModelAdmin):
    inlines = [
        ImageModelInline,
    ]


admin.site.register(models.ProductVariation, YourModelAdmin)
admin.site.register(models.Season)
admin.site.register(models.Filter)
admin.site.register(models.Order)
admin.site.register(models.ProductView)
admin.site.register(models.ProductImage)
