from django.db import models


# Create your models here.

class Project(models.Model):
    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'проекты'

    name = models.CharField(max_length=100)
    link = models.URLField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


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


class TrendYolDepartment(models.Model):
    class Meta:
        verbose_name = 'отделение (trendyol)'
        verbose_name_plural = 'отделения (trendyol)'

    name = models.CharField(max_length=100)
    link = models.URLField()
    brand = models.ForeignKey(Brand)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TrendYolCategory(models.Model):
    class Meta:
        verbose_name = 'категория (trendyol)'
        verbose_name_plural = 'категория (trendyol)'
    name = models.CharField(max_length=100)
    link = models.URLField()
    department = models.ForeignKey(TrendYolDepartment, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name