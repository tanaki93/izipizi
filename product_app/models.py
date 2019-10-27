from django.db import models

# Create your models here.
from django.utils.text import slugify

from projects_app.models import Project, Brand

from unidecode import unidecode


class Category(models.Model):
    class Meta:
        verbose_name = 'категорию'
        verbose_name_plural = 'категории'

    # parent = models.ForeignKey('self', null=True, blank=True)
    name = models.CharField(max_length=100)
    product_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     if self.parent is not None:
    #         self.tree_count = self.parent.tree_count + 1
    #     self.slug = unidecode(self.name)
    #     super(Category, self).save()


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
