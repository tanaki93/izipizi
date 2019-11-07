from django.db import models

# Create your models here.
from django.utils.text import slugify

from unidecode import unidecode


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

    def __str__(self):
        return self.name


class Department(models.Model):
    class Meta:
        verbose_name = 'отделение (izishop)'
        verbose_name_plural = 'отделения (izishop)'

    code = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(Department, self).save()


class Category(models.Model):
    class Meta:
        verbose_name = 'категорию (izishop)'
        verbose_name_plural = 'категории (izishop)'

    # parent = models.ForeignKey('self', null=True, blank=True)
    code = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(Category, self).save()


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

    def __str__(self):
        return self.url


class OriginalProduct(models.Model):
    class Meta:
        verbose_name_plural = 'товары (trendyol)'
        verbose_name = 'товар (trendyol)'

    title = models.CharField(max_length=100)
    product_id = models.CharField(max_length=100)
    variant_id = models.CharField(max_length=100, default='', blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True, default='')
    price = models.FloatField()
    original_price = models.FloatField()
    currency = models.CharField(max_length=100, default='TL')
    colour = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    tags = models.TextField()
    gender = models.CharField(max_length=100, default='М')
    rating = models.FloatField()
    status = models.IntegerField(default=1)
    delivery_info = models.CharField(max_length=100)
    link = models.OneToOneField(Link, null=True)
    delivery_fast = models.BooleanField(default=False)
    delivery_free = models.BooleanField(default=False)
    size = models.TextField()
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Currency(models.Model):
    class Meta:
        verbose_name_plural = 'Валюты'
        verbose_name = 'валюту'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
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
    product_id = models.CharField(max_length=100)
    variant_id = models.CharField(max_length=100, default='', blank=True)
    product_code = models.CharField(max_length=100, blank=True, null=True, default='')
    price = models.FloatField()
    original_price = models.FloatField()
    currency = models.CharField(max_length=100, default='TL')
    colour = models.CharField(max_length=100, blank=True, null=True)
    brand = models.ForeignKey(Brand)
    category = models.ForeignKey(Category)
    department = models.ForeignKey(Department, null=True)
    tags = models.TextField()
    gender = models.CharField(max_length=100, default='М')
    rating = models.FloatField()
    status = models.IntegerField(default=1)
    size = models.TextField()
    link = models.OneToOneField(Link, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
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
    category = models.ForeignKey(Category, null=True)

    def __str__(self):
        return self.name
