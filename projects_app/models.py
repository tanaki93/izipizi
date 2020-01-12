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
    (-1, 'NOT RECEIVED'),
    (1, 'RECEIVED'),
)

CHECKING_STATUSES = (
    (1, 'GOOD'),
    (-1, 'DEFECT'),
    (-2, 'ERROR'),
)

DELIVERY_STATUSES = (
    (1, 'WAITING'),
    (2, 'SEND'),
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
    date = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    name = models.CharField(max_length=100)
    payment_status = models.IntegerField(choices=PAYMENT_STATUSES, default=2, null=True, blank=True)
    process_status = models.IntegerField(choices=ORDER_PROCESS_STATUSES, default=1, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=100)
    phone = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True, blank=True)
    delivery_type = models.IntegerField(default=1, null=True, blank=True)
    property_type = models.IntegerField(default=1, null=True, blank=True)
    address = models.CharField(max_length=100)
    products_price = models.FloatField(null=True)
    total_price = models.FloatField(null=True)
    shipping_price = models.FloatField(null=True)


class OrderPackage(models.Model):
    number = models.CharField(max_length=100)
    status = models.IntegerField(choices=PACKAGE_STATUSES, default=1)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=SET_NULL, null=True)
    size = models.ForeignKey(VendSize, null=True)
    product = models.ForeignKey(OriginalProduct, null=True)
    price = models.FloatField(null=True)
    stage = models.CharField(null=True, max_length=100)
    package = models.ForeignKey(OrderPackage, null=True, blank=True)
    amount = models.IntegerField(default=1)
    product_status = models.IntegerField(default=2, choices=PROCESS_STATUSES, null=True)
    checking_status = models.IntegerField(default=1, choices=CHECKING_STATUSES, null=True)
    delivery_status = models.IntegerField(default=1, choices=DELIVERY_STATUSES, null=True)
    receive_date = models.DateTimeField(null=True, blank=True)
    send_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    logistic_receive_status = models.IntegerField(default=1, choices=PACKET_STATUSES, null=True)
    logistic_deliver_status = models.IntegerField(default=1, choices=SHIPPING_STATUSES, null=True)
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
    number = models.CharField(max_length=100, null=True)


class OrderPacket(models.Model):
    weight = models.IntegerField(null=True)
    flight = models.ForeignKey(Flight, null=True, on_delete=SET_NULL)
    status = models.IntegerField(null=True, choices=PACKET_STATUSES, default=1)
    received_status = models.IntegerField(null=True, choices=RECEIVING_STATUSES, default=-1)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


class PacketProduct(models.Model):
    order_item = models.ForeignKey(OrderItem, null=True, on_delete=SET_NULL)
    order_packet = models.ForeignKey(OrderPacket, null=True, on_delete=SET_NULL)
