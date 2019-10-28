from django.contrib import admin

# Register your models here.
from product_app.models import Category, Product, OriginalProduct, Tag, Size, Currency, Department, Brand, \
    TrendYolDepartment, TrendYolCategory

admin.site.register(Department)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Size)
admin.site.register(Currency)
admin.site.register(OriginalProduct)
admin.site.register(Brand)
admin.site.register(TrendYolDepartment)
admin.site.register(TrendYolCategory)
