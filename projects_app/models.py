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
    (1, 'WAITING'),
    (2, 'RECEIVED'),
    (-1, 'SENT BACK'),
)

SHIPPING_STATUSES = (
    (1, 'WAITING'),
    (2, 'SENT'),
    (3, 'RECEIVED'),
)

PACKAGE_STATUSES = (
    (1, 'ORDERED'),
    (2, 'RECEIVED'),
)

PACKET_STATUSES = (
    (1, 'WAITING'),
    (2, 'RECEIVED'),
)


class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    name = models.CharField(max_length=100)
    payment_status = models.IntegerField(choices=PAYMENT_STATUSES, default=2, null=True, blank=True)
    process_status = models.IntegerField(choices=ORDER_PROCESS_STATUSES, default=1, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)


class OrderPackage(models.Model):
    number = models.CharField(max_length=100)
    status = models.IntegerField(choices=PACKAGE_STATUSES, default=1)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=SET_NULL, null=True)
    size = models.ForeignKey(VendSize)
    product = models.ForeignKey(OriginalProduct)
    price = models.IntegerField(null=True)
    stage = models.CharField(null=True, max_length=100)
    package = models.ForeignKey(OrderPackage, null=True, blank=True)
    amount = models.IntegerField(default=1)
    product_status = models.IntegerField(default=1, choices=PROCESS_STATUSES)
    receiving_status = models.IntegerField(default=1, choices=RECEIVING_STATUSES)
    checking_status = models.IntegerField(default=1, choices=CHECKING_STATUSES)
    delivery_status = models.IntegerField(default=1, choices=DELIVERY_STATUSES)
    delivery_date = models.DateTimeField(null=True, blank=True)
    sending_date = models.DateTimeField(null=True, blank=True)
    shipping_status = models.IntegerField(default=1, choices=SHIPPING_STATUSES)
    shipping_date = models.DateTimeField(null=True, blank=True)
    shipping_service = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


class OrderItemComment(models.Model):
    order_item = models.ForeignKey(OrderItem, null=True, on_delete=SET_NULL)
    comment = models.TextField(null=True)


def file_upload_to(instance, filename):
    return "%s" % filename


class CommentImage(models.Model):
    image = models.ImageField(upload_to=file_upload_to, null=True)
    comment = models.ForeignKey(OrderItemComment, null=True, on_delete=SET_NULL)


class Flight(models.Model):
    number = models.CharField(max_length=100)


class OrderPacket(models.Model):
    weight = models.IntegerField(null=True)
    flight = models.ForeignKey(Flight, null=True, on_delete=SET_NULL)
    status = models.IntegerField(null=True, choices=PACKET_STATUSES, default=1)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


class PacketProduct(models.Model):
    order_item = models.ForeignKey(OrderItem, null=True, on_delete=SET_NULL)
    order_packet = models.ForeignKey(OrderPacket, null=True, on_delete=SET_NULL)
