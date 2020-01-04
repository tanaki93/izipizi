from django.db import models
from django.db.models import SET_NULL

from product_app.models import VendSize, OriginalProduct

PAYMENT_STATUSES = (
    (1, 'PAID'),
    (2, 'NOT PAID'),
)

ORDER_PROCESS_STATUSES = (
    (1, 'IN PROCESS'),
    (2, 'DONE'),
    (-1, 'CANCELED'),
)
PROCESS_STATUSES = (
    (1, 'WAITING'),
    (2, 'IN PROCESS'),
    (3, 'DONE'),
    (-1, 'CANCELED'),
)

RECEIVING_STATUSES = (
    (0, 'NOT RECEIVED'),
    (1, 'RECEIVED'),
)

CHECKING_STATUSES = (
    (1, 'GOOD'),
    (-1, 'DEFECT'),
    (-2, 'ERROR'),
)

DELIVERY_STATUSES = (
    (1, 'WAIT'),
    (2, 'SENT'),
    (-1, 'SENT BACK'),
)

SHIPPING_STATUSES = (
    (1, 'WAIT'),
    (2, 'SENT'),
)


class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    payment_status = models.IntegerField(choices=PAYMENT_STATUSES, default=2, null=True, blank=True)
    process_status = models.IntegerField(choices=ORDER_PROCESS_STATUSES, default=1, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=SET_NULL, null=True)
    size = models.ForeignKey(VendSize)
    product = models.ForeignKey(OriginalProduct)
    price = models.IntegerField(null=True)
    stage = models.CharField(null=True, max_length=100)
    amount = models.IntegerField(default=1)
    product_status = models.IntegerField(default=1, choices=PROCESS_STATUSES)
    receiving_status = models.IntegerField(default=1, choices=RECEIVING_STATUSES)
    checking_status = models.IntegerField(default=1, choices=CHECKING_STATUSES)
    delivery_status = models.IntegerField(default=1, choices=DELIVERY_STATUSES)
    shipping_status = models.IntegerField(default=1, choices=SHIPPING_STATUSES)
