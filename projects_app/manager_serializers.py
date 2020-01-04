from rest_framework import serializers

from product_app.models import VendSize
from projects_app.models import Order, OrderItem, OrderPackage, OrderItemComment, CommentImage
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


class PackageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPackage
        fields = '__all__'


class ImageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = '__all__'


class CommentItemSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemComment
        fields = 'comment id images'.split()

    def get_images(self, obj):
        return ImageItemSerializer(CommentImage.objects.filter(comment=obj), many=True).data


class OrderProductItemSerializer(serializers.ModelSerializer):
    size = VendSizeSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    package = PackageItemSerializer(read_only=True)
    package_status = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = 'id size product price amount product_status receiving_status checking_status delivery_status ' \
                 'shipping_status package_status stage package package_status comments'.split()

    def get_package_status(self, obj):
        package = obj.package
        if package is None:
            return 0
        else:
            return package.status

    def get_comments(self, obj):
        data = OrderItemComment.objects.filter(order_item=obj)
        return CommentItemSerializer(data, many=True).data


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


class PackageListSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = OrderPackage
        fields = 'id number updated created status products'.split()

    def get_products(self, obj):
        return OrderProductItemSerializer(OrderItem.objects.filter(package=obj), many=True).data
