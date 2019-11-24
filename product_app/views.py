from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from product_app.models import Category, Department, ParentCategory, Brand, Slider, Product
from product_app.serializers import CategorySerializer, ParentCategorySerializer, BrandSerializer, DepartmentSerializer, \
    SliderSerializer, ProductSerializer
from user_app.permissions import IsAdmin


@api_view(['GET'])
@permission_classes([AllowAny])
def categories_list_view(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(categories, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_departments_view(request):
    if request.method == 'GET':
        departments = Department.objects.all()
        return Response(status=status.HTTP_200_OK, data=DepartmentSerializer(departments, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_categories_view(request):
    if request.method == 'GET':
        categories = ParentCategory.objects.all()
        return Response(status=status.HTTP_200_OK, data=ParentCategorySerializer(categories, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_categories_top_view(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(categories, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_brands_view(request):
    if request.method == 'GET':
        brands = Brand.objects.all()
        return Response(status=status.HTTP_200_OK, data=BrandSerializer(brands, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_sliders_view(request):
    sliders = Slider.objects.all()[0:6]
    if request.method == 'GET':
        return Response(status=status.HTTP_200_OK, data=SliderSerializer(sliders, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_products_view(request):
    if request.method == 'GET':
        products = Product.objects.all()
        brand_id = None
        try:
            brand_id = int(request.GET.get('brand_id'))
        except:
            pass
        if brand_id is not None:
            products = products.filter(brand_id=brand_id)
        parent_category_id = None
        try:
            parent_category_id = int(request.GET.get('parent_category_id'))
        except:
            pass
        if parent_category_id is not None:
            products = products.filter(category__parent_id=parent_category_id)
        category_id = None
        try:
            category_id = int(request.GET.get('category_id'))
        except:
            pass
        if category_id is not None:
            products = products.filter(category_id=category_id)
        pages = products.count() // 16
        if products.count() % 16 != 0:
            pages += 1
        page = 1
        try:
            page = int(request.GET.get('page', '1'))
        except:
            pass
        data = {
            'data': {
                'pages': pages,
                'page': page,
                'count': products.count(),
            },
            'objects': ProductSerializer(products[(page - 1) * 16: page * 16], many=True).data
        }
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_products_item_view(request, id):
    if request.method=='GET':
        try:
            product = Product.objects.get(id = id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data=ProductSerializer(product).data, status=status.HTTP_200_OK)
