from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from product_app.models import Category
from product_app.serializers import CategorySerializer
from user_app.permissions import IsAdmin


@api_view(['GET'])
@permission_classes([AllowAny])
def categories_list_view(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(categories, many=True).data)
