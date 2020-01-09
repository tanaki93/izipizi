import datetime

from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from projects_app.manager_serializers import OrderListSerializer, OrderItemSerializer, PackageListSerializer, \
    OrderProductItemSerializer, PacketListSerializer, OrderLogisticSerializer, OrderItemLogisticSerializer
from projects_app.models import Order, OrderItem, OrderPackage, OrderItemComment, CommentImage, OrderPacket, \
    PacketProduct, Flight


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def manager_orders_view(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        date_from = None
        try:
            date_from = datetime.datetime.strptime(request.GET.get('date_from'), "%Y-%m-%d")
        except:
            pass
        if date_from is not None:
            orders = orders.filter(date__gte=date_from)
        date_to = None
        try:
            date_to = datetime.datetime.strptime(request.GET.get('date_to'), "%Y-%m-%d")
        except:
            pass
        if date_to is not None:
            orders = orders.filter(date__lte=date_to)
        id = None
        try:
            id = int(request.GET.get('id'))
        except:
            pass
        if id is not None:
            orders = orders.filter(id=id)

        name = None
        try:
            name = (request.GET.get('name'))
        except:
            pass
        if name is not None:
            orders = orders.filter(name__icontains=name)
        data = OrderListSerializer(orders, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET'])
@permission_classes([AllowAny])
def manager_clients_view(request):
    if request.method == 'GET':
        name = request.GET.get('name', '')
        orders = Order.objects.filter(name__icontains=name)
        data = []
        for i in orders:
            if i.name not in data:
                data.append(i.name)
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([AllowAny])
def manager_orders_item_view(request, id):
    order = Order.objects.get(id=id)
    if request.method == 'GET':
        data = OrderItemSerializer(order).data
        return Response(status=status.HTTP_200_OK, data=data)
    elif request.method == 'POST':
        status_process = None
        try:
            status_process = int(request.data.get('status'))
        except:
            pass
        if status_process is not None:
            order.process_status = status_process
            order.save()
            return Response(status=status.HTTP_200_OK, data=OrderItemSerializer(order).data)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)




@api_view(['PUT', 'POST'])
@permission_classes([AllowAny])
def manager_orders_product_item_view(request, id):
    order_item = OrderItem.objects.get(id=id)
    if request.method == 'PUT':
        option = request.data.get('option')
        value = request.data.get('value')
        if option == 'product_status':
            order_item.product_status = value
        if option == 'delivery_status':
            order_item.delivery_status = value
        if option == 'receiving_status':
            order_item.receiving_status = value
        if option == 'shipping_status':
            order_item.shipping_status = value
        if option == 'checking_status':
            order_item.checking_status = value
        order_item.save()
    elif request.method == 'POST':
        stage = request.data.get('stage', '')
        order_item.stage = stage
        if stage != '':
            package = None
            try:
                package = OrderPackage.objects.filter(number=stage)[0]
            except:
                pass
            if package is None:
                package = OrderPackage.objects.create(number=stage)
            order_item.package = package
        else:
            order_item.package = None
        order_item.save()
    return Response(status=status.HTTP_200_OK, data=OrderProductItemSerializer(order_item).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def manager_packages_view(request):
    if request.method == 'GET':
        packages = OrderPackage.objects.filter(orderitem__isnull=False)
        date_from = None
        try:
            date_from = datetime.datetime.strptime(request.GET.get('date_from'), "%Y-%m-%d")
        except:
            pass
        if date_from is not None:
            packages = packages.filter(created__gte=date_from)
        date_to = None
        try:
            date_to = datetime.datetime.strptime(request.GET.get('date_to'), "%Y-%m-%d")
        except:
            pass
        if date_to is not None:
            packages = packages.filter(created__lte=date_to)
        number = ''
        try:
            number = str(request.GET.get('number', ''))
        except:
            pass
        if number != '':
            packages = packages.filter(number=number)
        return Response(PackageListSerializer(packages, many=True).data, status=status.HTTP_200_OK)


@api_view(['PUT', 'GET'])
@permission_classes([AllowAny])
def manager_packages_item_view(request, id):
    package = OrderPackage.objects.get(id=id)
    if request.method == 'PUT':
        statuses = int(request.data.get('status', 1))
        package.status = statuses
        package.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'GET':
        return Response(PackageListSerializer(package).data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def manager_checking_product_view(request):
    if request.method == 'GET':
        orders = OrderItem.objects.filter(delivery_status=2, package__isnull=False,
                                          packetproduct__order_packet__isnull=True)
        date_from = None
        try:
            date_from = datetime.datetime.strptime(request.GET.get('date_from'), "%Y-%m-%d")
        except:
            pass

        if date_from is not None:
            orders = orders.filter(updated__gte=date_from)
        date_to = None
        try:
            date_to = datetime.datetime.strptime(request.GET.get('date_to'), "%Y-%m-%d")
        except:
            pass
        if date_to is not None:
            orders = orders.filter(updated__lte=date_to)
        number = ''
        try:
            number = (request.GET.get('number', ''))
        except:
            pass
        if number != '':
            orders = orders.filter(package__number=number)
        data = OrderProductItemSerializer(orders, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)
    elif request.method == 'POST':
        products = request.data.get('order_products')
        weight = None
        try:
            weight = int(request.data.get('weight'))
        except:
            pass
        if weight is not None:
            order_packet = OrderPacket.objects.create(weight=weight)
            order_packet.save()
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        if products is not None:
            for i in products:
                try:
                    order_item = OrderItem.objects.get(id=int(i))
                    # order_item.delivery_status = 3  # отправлен
                    packet_product = PacketProduct.objects.create(order_item=order_item, order_packet=order_packet)
                    packet_product.save()
                except:
                    pass
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['PUT', 'GET', 'POST'])
@permission_classes([AllowAny])
def manager_checking_item_product_view(request, id):
    item = OrderItem.objects.get(id=id)
    if request.method == 'PUT':
        statuses = int(request.data.get('status', 1))
        item.checking_status = statuses
        item.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'GET':
        return Response(OrderProductItemSerializer(item).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        comment = request.data.get('comment', '')
        new_comment = OrderItemComment.objects.create(order_item=item, comment=comment)
        new_comment.save()
        try:
            images = request.FILES['images']
            fs = FileSystemStorage()
            for image in images:
                filename = fs.save(image.name, image)
                comment_image = CommentImage.objects.create(comment=new_comment, image=filename)
                comment_image.save()
        except:
            pass
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def manager_packets_view(request):
    if request.method == 'GET':
        packages = OrderPacket.objects.all()
        date_from = None
        try:
            date_from = datetime.datetime.strptime(request.GET.get('date_from'), "%Y-%m-%d")
        except:
            pass
        if date_from is not None:
            packages = packages.filter(created__gte=date_from)
        date_to = None
        try:
            date_to = datetime.datetime.strptime(request.GET.get('date_to'), "%Y-%m-%d")
        except:
            pass
        if date_to is not None:
            packages = packages.filter(created__lte=date_to)
        number = ''
        try:
            number = str(request.GET.get('number', ''))
        except:
            pass
        if number != '':
            packages = packages.filter(packetproduct__order_item__package__number__icontains=number)
        return Response(PacketListSerializer(packages, many=True).data, status=status.HTTP_200_OK)


@api_view(['PUT', 'POST'])
@permission_classes([AllowAny])
def manager_packet_item_view(request, id):
    order_packet = OrderPacket.objects.get(id=id)
    if request.method == 'PUT':
        order_packet.received_status = int(request.data.get('received_status', 1))
        order_packet.save()
    elif request.method == 'POST':
        flight_number = request.data.get('flight_number', '')
        if flight_number != '':
            flight = None
            try:
                flight = Flight.objects.filter(number=flight_number)[0]
            except:
                pass
            if flight is None:
                flight = Flight.objects.create(number=flight_number)
                flight.save()
            order_packet.flight = flight
        else:
            order_packet.flight = None
        order_packet.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def manager_logistics_orders_view(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        date_from = None
        try:
            date_from = datetime.datetime.strptime(request.GET.get('date_from'), "%Y-%m-%d")
        except:
            pass
        if date_from is not None:
            orders = orders.filter(date__gte=date_from)
        date_to = None
        try:
            date_to = datetime.datetime.strptime(request.GET.get('date_to'), "%Y-%m-%d")
        except:
            pass
        if date_to is not None:
            orders = orders.filter(date__lte=date_to)
        number = None
        try:
            number = (request.GET.get('number'))
        except:
            pass
        if number is not None:
            orders = orders.filter(orderitem__package__number__icontains=number)
        data = OrderLogisticSerializer(orders, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['PUT', 'POST'])
@permission_classes([AllowAny])
def manager_logistic_product_item_view(request, id):
    order_item = OrderItem.objects.get(id=id)
    if request.method == 'PUT':
        option = request.data.get('option')
        value = request.data.get('value')
        if option == 'delivery_status':
            order_item.delivery_status = value
            order_item.save()
            if value == 2:
                order_item.delivery_date = order_item.updated
                order_item.save()
        if option == 'shipping_status':
            order_item.shipping_status = value
            order_item.save()
            if value == 3:
                order_item.delivery_date = order_item.updated
                order_item.save()
            elif value == 2:
                order_item.sending_date = order_item.updated
                order_item.save()
        order_item.save()
    elif request.method == 'POST':
        shipping_service = request.data.get('shipping_service', '')
        order_item.shipping_service = shipping_service
        order_item.shipping_status = 2
        order_item.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([AllowAny])
def manager_orders_logistic_item_view(request, id):
    order = Order.objects.get(id=id)
    if request.method == 'GET':
        data = OrderItemLogisticSerializer(order).data
        return Response(status=status.HTTP_200_OK, data=data)
    elif request.method == 'POST':
        status_process = None
        try:
            status_process = int(request.data.get('status'))
        except:
            pass
        if status_process is not None:
            order.process_status = status_process
            order.save()
            return Response(status=status.HTTP_200_OK, data=OrderItemLogisticSerializer(order).data)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)