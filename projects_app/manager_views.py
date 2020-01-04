from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from projects_app.manager_serializers import OrderListSerializer, OrderItemSerializer
from projects_app.models import Order


@api_view(['GET'])
@permission_classes([AllowAny])
def manager_orders_view(request):
    if request.method == 'GET':
        data = OrderListSerializer(Order.objects.all(), many=True).data
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


@api_view(['GET'])
@permission_classes([AllowAny])
def manager_orders_item_view(request, id):
    if request.method == 'GET':
        data = OrderItemSerializer(Order.objects.get(id=id)).data
        return Response(status=status.HTTP_200_OK, data=data)