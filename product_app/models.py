from django.db import models

# Create your models here.
from django.db.models import SET_NULL
from django.utils.text import slugify

from unidecode import unidecode

from user_app.models import User


def file_upload_to(instance, filename):
    return "%s" % filename


OUT_PROCESS = 1
PROCESSED = 2
IN_PROCESS = 3
NOT_PARSED = 4
STATUSES = (
    (OUT_PROCESS, 'Необработан'),
    (PROCESSED, 'Обработан'),
    (IN_PROCESS, 'В обработке'),
    (NOT_PARSED, 'Неспарсен'),
)


class Brand(models.Model):
    class Meta:
        verbose_name = 'бренд'
        verbose_name_plural = 'бренды'

    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_trend_yol = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=file_upload_to, null=True, blank=True)

    def __str__(self):
        return self.name


class Slider(models.Model):
    title = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = 'Слайдер'
        verbose_name_plural = 'сдайдеры'

    def __str__(self):
        return self.title


class ImageSlider(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to=file_upload_to)
    slider = models.ForeignKey(Slider, blank=True, null=True, related_name='images')

    def __str__(self):
        return self.image.name


class Department(models.Model):
    class Meta:
        verbose_name = 'отделение (izishop)'
        verbose_name_plural = 'отделения (izishop)'

    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(Department, self).save()


class ParentCategory(models.Model):
    class Meta:
        verbose_name = 'род. категорию (izishop)'
        verbose_name_plural = 'род. категории (izishop)'

    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(ParentCategory, self).save()


class Category(models.Model):
    class Meta:
        verbose_name = 'категорию (izishop)'
        verbose_name_plural = 'категории (izishop)'

    parent = models.ForeignKey(ParentCategory, null=True, blank=True, related_name='childs')
    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to=file_upload_to, null=True, blank=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(Category, self).save()


class Document(models.Model):
    class Meta:
        verbose_name = 'документ'
        verbose_name_plural = 'документы'

    original_products = models.ManyToManyField('OriginalProduct')
    user = models.ForeignKey(User)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.updated_at.__str__()


class Tag(models.Model):
    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Link(models.Model):
    class Meta:
        verbose_name_plural = 'Ссылка'
        verbose_name = 'Ссылки'

    url = models.URLField()
    tr_category = models.ForeignKey('TrendYolCategory', null=True, related_name='tr_categories')
    status = models.IntegerField(default=4, choices=STATUSES)

    def __str__(self):
        return self.url


class OriginalProduct(models.Model):
    class Meta:
        verbose_name_plural = 'товары (trendyol)'
        verbose_name = 'товар (trendyol)'

    title = models.CharField(max_length=100)
    product_id = models.CharField(max_length=100)
    product_code = models.CharField(max_length=100, blank=True, null=True, default='')
    discount_price = models.FloatField(null=True, blank=True)
    selling_price = models.FloatField(null=True, blank=True)
    original_price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=100, default='TL')
    colour = models.CharField(max_length=100, blank=True, null=True)
    # status = models.IntegerField(default=1)
    link = models.OneToOneField(Link, null=True, related_name='originalproduct')
    is_rush_delivery = models.BooleanField(default=False)
    is_free_argo = models.BooleanField(default=False)
    delivery_date = models.TextField(null=True, blank=True)
    images = models.TextField(null=True, blank=True)
    promotions = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# class ProductImage(models.Model):
#     url = models.CharField(max_length=100)
#     original_product = models.ForeignKey(OriginalProduct, related_name='images')


class Variant(models.Model):
    class Meta:
        verbose_name_plural = 'Варианты'
        verbose_name = 'вариант'

    tr_size = models.ForeignKey('TrendyolSize', null=True)
    original_product = models.ForeignKey(OriginalProduct, related_name='variants')
    stock = models.BooleanField(default=False)

    def __str__(self):
        return self.tr_size.name


class Currency(models.Model):
    class Meta:
        verbose_name_plural = 'Валюты'
        verbose_name = 'валюту'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, default='TRY')
    rate = models.FloatField()

    def __str__(self):
        return self.name


class TrendyolSize(models.Model):
    class Meta:
        verbose_name_plural = 'Размер (trendyol)'
        verbose_name = 'Размеры (trendyol)'

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(TrendyolSize, self).save()


class Size(models.Model):
    class Meta:
        verbose_name_plural = 'Размер (izishop)'
        verbose_name = 'Размеры (izishop)'

    trendyol_size = models.OneToOneField(TrendyolSize, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        verbose_name_plural = 'товары (izishop)'
        verbose_name = 'товар (izishop)'

    title = models.CharField(max_length=100)
    title_lower = models.CharField(max_length=100, null=True, blank=True)
    link = models.OneToOneField(Link, null=True)
    discount_price = models.FloatField(null=True, blank=True)
    selling_price = models.FloatField(null=True, blank=True)
    original_price = models.FloatField(null=True, blank=True)
    description = models.TextField()
    description_lower = models.TextField(null=True, blank=True)
    colour = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    brand = models.ForeignKey('Brand', null=True, blank=True)
    department = models.ForeignKey('Department', null=True, blank=True)
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.title_lower = self.title.lower()
        self.description_lower = self.description.lower()
        super(Product, self).save()

    def __str__(self):
        return self.title


class TrendYolDepartment(models.Model):
    class Meta:
        verbose_name = 'отделение (trendyol)'
        verbose_name_plural = 'отделения (trendyol)'

    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, null=True)
    brand = models.ForeignKey(Brand)
    is_active = models.BooleanField(default=True)
    department = models.ForeignKey(Department, null=True)

    def __str__(self):
        return self.name


class TrendYolCategory(models.Model):
    class Meta:
        verbose_name = 'категория (trendyol)'
        verbose_name_plural = 'категории (trendyol)'

    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(TrendYolDepartment, null=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=SET_NULL)

    def __str__(self):
        return self.name
