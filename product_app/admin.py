from django.contrib import admin

# Register your models here.
from product_app.models import Category, Product, OriginalProduct, Tag, TrendyolSize, Currency, Department, Brand, \
    TrendYolDepartment, TrendYolCategory, Size, Link, Variant, Document, ParentCategory, Slider, ImageSlider


class OriginalProductAdmin(admin.ModelAdmin):
    model = OriginalProduct
    # exclude = 'link'.split()
    readonly_fields = 'link'.split()


class ProductAdmin(admin.ModelAdmin):
    model = Product
    # exclude = 'link'.split()
    readonly_fields = 'link'.split()
    list_display = 'id title link'.split()


class LinkAdmin(admin.ModelAdmin):
    model = Link
    search_fields = 'url'.split()
    list_display = 'id url tr_category'.split()


class ImageInline(admin.StackedInline):
    model = ImageSlider
    extra = 0


class SliderAdmin(admin.ModelAdmin):
    model = Slider
    inlines = [ImageInline]


admin.site.register(Department)
admin.site.register(Category)
admin.site.register(ParentCategory)
admin.site.register(Product, ProductAdmin)
admin.site.register(Tag)
admin.site.register(Slider, SliderAdmin)
admin.site.register(Document)
admin.site.register(TrendyolSize)
admin.site.register(Size)
admin.site.register(Link, LinkAdmin)
admin.site.register(Currency)
admin.site.register(OriginalProduct, OriginalProductAdmin)
admin.site.register(Brand)
admin.site.register(TrendYolDepartment)
admin.site.register(TrendYolCategory)
admin.site.register(Variant)
