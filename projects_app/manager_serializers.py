from rest_framework import serializers

from product_app.models import VendSize
from projects_app.models import Order, OrderItem
from projects_app.serializers import VendSizeSerializer, ProductSerializer


class OrderListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = 'id date name payment_status process_status email phone address price statuses count'.split()

    def get_price(self, obj):
        items = OrderItem.objects.filter(order=obj)
        price = 0
        for i in items:
            price += i.price
        return price

    def get_count(self, obj):
        return OrderItem.objects.filter(order=obj).count()

    def get_statuses(self, obj):
        data = {
            'waiting': OrderItem.objects.filter(order=obj, product_status=1).count(),
            'in_process': OrderItem.objects.filter(order=obj, product_status=2).count(),
            'done': OrderItem.objects.filter(order=obj, product_status=3).count(),
            'cancelled': OrderItem.objects.filter(order=obj, product_status=4).count(),
        }
        return data


class OrderProductItemSerializer(serializers.ModelSerializer):
    size = VendSizeSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = 'id size product price amount product_status receiving_status checking_status delivery_status ' \
                 'shipping_status stage'.split()


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = 'id date name payment_status process_status email phone address price products statuses count'.split()

    def get_count(self, obj):
        return OrderItem.objects.filter(order=obj).count()

    def get_statuses(self, obj):
        data = {
            'waiting': OrderItem.objects.filter(order=obj, product_status=1).count(),
            'in_process': OrderItem.objects.filter(order=obj, product_status=2).count(),
            'done': OrderItem.objects.filter(order=obj, product_status=3).count(),
            'cancelled': OrderItem.objects.filter(order=obj, product_status=4).count(),
        }
        return data

    def get_price(self, obj):
        items = OrderItem.objects.filter(order=obj)
        price = 0
        for i in items:
            price += i.price
        return price

    def get_products(self, obj):
        data = OrderProductItemSerializer(OrderItem.objects.filter(order=obj), many=True).data
        return data
