from django.db import models

# Create your models here.
from django.utils.text import slugify

from unidecode import unidecode


class Brand(models.Model):
    class Meta:
        verbose_name = 'бренд'
        verbose_name_plural = 'бренды'

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    class Meta:
        verbose_name = 'отделение'
        verbose_name_plural = 'отделении'

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
        verbose_name = 'категорию'
        verbose_name_plural = 'категории'

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


class OriginalProduct(models.Model):
    class Meta:
        verbose_name_plural = 'товары (оригинал)'
        verbose_name = 'товар (оригинал)'

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


class Size(models.Model):
    name = models.CharField(max_length=100)


class Product(models.Model):
    class Meta:
        verbose_name_plural = 'товары'
        verbose_name = 'товар'

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
        verbose_name_plural = 'категория (trendyol)'

    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(TrendYolDepartment, null=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, null=True)

    def __str__(self):
        return self.name
