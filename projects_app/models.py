from django.db import models
from django.db.models import SET_NULL

from product_app.models import VendSize, OriginalProduct

PAYMENT_STATUSES = (
    (1, 'PAID'),
    (2, 'NOT PAID'),
)

PROCESS_STATUSES = (
    (1, 'WAITING'),
    (2, 'IN PROCESS'),
    (3, 'DONE'),
    (4, 'CANCELED'),
)


class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    payment_status = models.IntegerField(choices=PAYMENT_STATUSES, default=2, null=True, blank=True)
    process_status = models.IntegerField(choices=PAYMENT_STATUSES, default=1, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=SET_NULL, null=True)
    size = models.ForeignKey(VendSize)
    product = models.ForeignKey(OriginalProduct)
    price = models.IntegerField(null=True)
    amount = models.IntegerField(default=1)