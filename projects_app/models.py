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
