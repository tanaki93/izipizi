from django.db import models

# Create your models here.
from django.db.models import SET_NULL
from django.db.models.signals import post_save
from django.dispatch import receiver
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


class Project(models.Model):
    class Meta:
        verbose_name_plural = 'Проекты'
        verbose_name = 'проект'

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Language(models.Model):
    class Meta:
        verbose_name_plural = 'языки'
        verbose_name = 'язык'

    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    is_translate = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Currency(models.Model):
    class Meta:
        verbose_name_plural = 'Валюты'
        verbose_name = 'валюту'

    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    code_name = models.CharField(max_length=10, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ExchangeRate(models.Model):
    class Meta:
        verbose_name = 'обмен валют'
        verbose_name_plural = 'обмен валют'

    value = models.FloatField()
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    date = models.DateField(null=True, blank=True)
    from_currency = models.ForeignKey(Currency, related_name='from_currency', null=True)
    to_currency = models.ForeignKey(Currency, related_name='to_currency', null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.value)


class ExchangeValue(models.Model):
    class Meta:
        ordering = '-updated_at'.split()

    exchange = models.ForeignKey(ExchangeRate, related_name='values')
    value = models.FloatField()
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    date = models.DateField(null=True, blank=True)


# @receiver(post_save, sender=ExchangeRate, dispatch_uid="update_stock_count")
# def update_stock(sender, instance, **kwargs):
#     exchange_value = ExchangeValue.objects.create(value=instance.value, exchange=instance, date=instance.date)
#     exchange_value.save()


class Country(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    language = models.ForeignKey(Language, null=True, on_delete=SET_NULL)
    currency = models.ForeignKey(Currency, null=True, on_delete=SET_NULL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class VendColour(models.Model):
    class Meta:
        verbose_name = 'Цвет (vend)'
        verbose_name_plural = 'цвет (vend)'

    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    izi_colour = models.ForeignKey('IziColour', null=True, blank=True, on_delete=SET_NULL)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(VendColour, self).save()


class IziColour(models.Model):
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(IziColour, self).save()


class TranslationColour(models.Model):
    language = models.ForeignKey(Language, null=True)
    colour = models.ForeignKey(IziColour, null=True, blank=True, related_name='translations')
    name = models.CharField(max_length=100, default='')
    name_lower = models.CharField(max_length=100, default='', null=True)

    def save(self, *args, **kwargs):
        # self.name_lower = self.name.lower()
        super(TranslationColour, self).save()

    def __str__(self):
        return self.name


class Brand(models.Model):
    class Meta:
        verbose_name = 'бренд'
        verbose_name_plural = 'бренды'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_trend_yol = models.BooleanField(default=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    currency = models.ForeignKey(Currency, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=file_upload_to, null=True, blank=True)

    def __str__(self):
        return self.name


class BrandCountry(models.Model):
    country = models.ForeignKey(Country, null=True)
    brand = models.ForeignKey(Brand, null=True)
    is_active = models.BooleanField(default=True)
    mark_up = models.FloatField()
    round_digit = models.IntegerField(default=2)
    round_to = models.CharField(max_length=10, default='00', null=True)


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
    position = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(Department, self).save()


class TranslationDepartment(models.Model):
    class Meta:
        verbose_name = 'отделение (перевод)'
        verbose_name_plural = 'отделения (перевод)'

    department = models.ForeignKey(Department, null=True)
    name = models.CharField(max_length=100, null=True)
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    language = models.ForeignKey(Language, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(TranslationDepartment, self).save()


class ParentCategory(models.Model):
    class Meta:
        ordering = 'position'.split()
        verbose_name = 'род. категорию (izishop)'
        verbose_name_plural = 'род. категории (izishop)'

    name = models.CharField(max_length=100, default='')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=SET_NULL)
    code = models.CharField(max_length=100, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    name_lower = models.CharField(max_length=100, null=True, blank=True, default='')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            self.name_lower = str(self.name).lower()
        except:
            self.name_lower = ''
            pass
        super(ParentCategory, self).save()


class TranslationParentCategory(models.Model):
    class Meta:
        verbose_name = 'род. категорию (перевод)'
        verbose_name_plural = 'род. категории (перевод)'

    parent_category = models.ForeignKey(ParentCategory, on_delete=SET_NULL, null=True)
    language = models.ForeignKey(Language, null=True)
    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(TranslationParentCategory, self).save()


class Category(models.Model):
    class Meta:
        verbose_name = 'категорию (izishop)'
        verbose_name_plural = 'категории (izishop)'

    parent = models.ForeignKey(ParentCategory, null=True, blank=True, related_name='childs', on_delete=SET_NULL)
    name = models.CharField(max_length=100)
    position = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to=file_upload_to, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(Category, self).save()


class TranslationCategory(models.Model):
    class Meta:
        verbose_name = 'категорию (перевод)'
        verbose_name_plural = 'категории (перевод)'

    category = models.ForeignKey(Category, null=True, blank=True, related_name='translations', on_delete=SET_NULL)
    name = models.CharField(max_length=100)
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    language = models.ForeignKey(Language, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super(TranslationCategory, self).save()


class Document(models.Model):
    class Meta:
        verbose_name = 'документ'
        verbose_name_plural = 'документы'

    user = models.ForeignKey(User, null=True, blank=True, on_delete=SET_NULL)
    department = models.ForeignKey('VendDepartment', null=True, blank=True)
    brand = models.ForeignKey('Brand', null=True, blank=True)
    status = models.IntegerField(default=1)
    step = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.updated_at.__str__()


class DocumentProduct(models.Model):
    product = models.ForeignKey('OriginalProduct', null=True, related_name='document_product')
    document = models.ForeignKey(Document, null=True, blank=True)
    step = models.IntegerField(default=1, null=True, blank=True)


class DocumentComment(models.Model):
    document = models.ForeignKey(Document, null=True, blank=True, related_name='comments')
    text = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


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
    tr_category = models.ForeignKey('VendCategory', null=True, related_name='tr_categories', on_delete=SET_NULL)
    status = models.IntegerField(default=4, choices=STATUSES)

    def __str__(self):
        return self.url


class OriginalProduct(models.Model):
    class Meta:
        verbose_name_plural = 'товары (vend)'
        verbose_name = 'товар (vend)'

    title = models.CharField(max_length=100)
    title_lower = models.CharField(max_length=100, null=True, blank=True)
    product_id = models.CharField(max_length=100)
    product_code = models.CharField(max_length=100, blank=True, null=True, default='')
    discount_price = models.FloatField(null=True, blank=True)
    selling_price = models.FloatField(null=True, blank=True)
    original_price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=100, default='TL')
    colour = models.ForeignKey('VendColour', blank=True, null=True)
    colour_code = models.CharField(max_length=100, blank=True, null=True)
    # status = models.IntegerField(default=1)
    link = models.OneToOneField(Link, null=True, related_name='originalproduct', on_delete=SET_NULL)
    brand = models.ForeignKey('Brand', null=True, blank=True, on_delete=SET_NULL)
    department = models.ForeignKey('VendDepartment', null=True, blank=True, on_delete=SET_NULL)
    category = models.ForeignKey('VendCategory', null=True, blank=True, on_delete=SET_NULL)
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

    def save(self, *args, **kwargs):
        self.title_lower = self.title.lower()
        super(OriginalProduct, self).save()


# class ProductImage(models.Model):
#     url = models.CharField(max_length=100)
#     original_product = models.ForeignKey(OriginalProduct, related_name='images')


class Variant(models.Model):
    class Meta:
        verbose_name_plural = 'Варианты'
        verbose_name = 'вариант'

    tr_size = models.ForeignKey('VendSize', null=True)
    original_product = models.ForeignKey(OriginalProduct, related_name='variants', on_delete=SET_NULL, null=True)
    stock = models.BooleanField(default=False)

    def __str__(self):
        return self.tr_size.name


class VendSize(models.Model):
    class Meta:
        verbose_name_plural = 'Размер (vend)'
        verbose_name = 'Размеры (vend)'

    name = models.CharField(max_length=100)
    izi_size = models.ForeignKey('Size', null=True, on_delete=SET_NULL)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(VendSize, self).save()


class Size(models.Model):
    class Meta:
        verbose_name_plural = 'Размер (izishop)'
        verbose_name = 'Размеры (izishop)'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, null=True, blank=True, default='')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TranslationSize(models.Model):
    class Meta:
        verbose_name = 'размер (перевод)'
        verbose_name_plural = 'размер (перевод)'

    size = models.ForeignKey(Size, null=True, blank=True, related_name='translations', on_delete=SET_NULL)
    name = models.CharField(max_length=100, null=True, blank=True)
    name_lower = models.CharField(max_length=100, null=True, blank=True)
    language = models.ForeignKey(Language, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # self.name_lower = self.name.lower()
        super(TranslationSize, self).save()


class Product(models.Model):
    class Meta:
        verbose_name_plural = 'товары (izishop)'
        verbose_name = 'товар (izishop)'

    title = models.CharField(max_length=100)
    title_lower = models.CharField(max_length=100, null=True, blank=True)
    link = models.OneToOneField(Link, null=True, on_delete=SET_NULL)
    description = models.TextField()
    description_lower = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    department = models.ForeignKey('Department', null=True, blank=True, on_delete=SET_NULL)
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=SET_NULL)
    colour = models.ForeignKey('IziColour', null=True, blank=True, on_delete=SET_NULL)

    def save(self, *args, **kwargs):
        self.title_lower = self.title.lower()
        self.description_lower = self.description.lower()
        super(Product, self).save()

    def __str__(self):
        return self.title


class VendDepartment(models.Model):
    class Meta:
        verbose_name = 'отделение (vend)'
        verbose_name_plural = 'отделения (vend)'

    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, null=True)
    brand = models.ForeignKey(Brand, related_name='brand', on_delete=SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    department = models.ForeignKey(Department, null=True, related_name='departments')

    def __str__(self):
        return self.name


class VendCategory(models.Model):
    class Meta:
        verbose_name = 'категория (vend)'
        verbose_name_plural = 'категории (vend)'

    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(VendDepartment, null=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=SET_NULL, related_name='categories')

    def __str__(self):
        return self.name
