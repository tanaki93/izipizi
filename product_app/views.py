import json

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from product_app.models import Category, Department, ParentCategory, Brand, Slider, Product, OriginalProduct, \
    VendColour, BrandCountry, ExchangeRate, VendSize, IziColour, Size
from product_app.serializers import CategorySerializer, ParentCategorySerializer, BrandSerializer, DepartmentSerializer, \
    SliderSerializer, MainProductSerializer
from projects_app.serializers import MainColourSerializer, VendSizeSerializer, IziSizeSerializer
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


def get_price(price):
    try:
        brand_country = BrandCountry.objects.all().first()
        exchange = ExchangeRate.objects.all().first()
        x = (price / exchange.value)
        return x / brand_country.mark_up
    except:
        return 0


@api_view(['GET'])
@permission_classes([AllowAny])
def client_search_view(request):
    if request.method == 'GET':
        query = None
        try:
            query = (request.GET.get('query', ''))
        except:
            pass
        brands = Brand.objects.filter(name__icontains=query)
        categories = Category.objects.filter(name__icontains=query)
        data = []
        for brand in brands:
            context = {
                'option': 'brand',
                'id': brand.id,
                'name': brand.name
            }
            data.append(context)
        for category in categories:
            context = {
                'option': 'category',
                'id': category.id,
                'name': category.name
            }
            data.append(context)
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_products_view(request):
    if request.method == 'GET':
        products = OriginalProduct.objects.filter(document_product__document__step=100)
        brand_id = None
        try:
            brand_id = int(request.GET.get('brand_id'))
        except:
            pass

        if brand_id is not None:
            products = products.filter(brand_id=brand_id)
        js = []
        try:
            brands = str(request.GET.get('brands'))
            js = list(json.loads(brands))
        except:
            pass

        if len(js) > 0:
            products = products.filter(brand_id__in=js)
        js = []
        try:
            sizes = str(request.GET.get('sizes', '')).strip()
            if len(sizes) > 2:
                sizes_arr = sizes[1: len(sizes) - 1].split(',')
                js = [i.strip().upper() for i in sizes_arr]
        except:
            pass
        if len(js) > 0:
            products = products.filter(variants__tr_size__izi_size__name__in=js)
        price_from = None
        try:
            price_from = int(request.GET.get('price_from'))
        except:
            pass
        if price_from is not None:
            products = products.filter(discount_price__gte=get_price(price_from))

        price_to = None
        try:
            price_to = int(request.GET.get('price_to'))
        except:
            pass
        if price_to is not None:
            products = products.filter(discount_price__lte=get_price(price_to))

        department_id = None
        try:
            department_id = int(request.GET.get('department_id'))
        except:
            pass
        if department_id is not None:
            products = products.filter(link__product__department_id=department_id)

        colour_id = None
        try:
            colour_id = int(request.GET.get('colour_id'))
        except:
            pass
        if colour_id is not None:
            products = products.filter(link__product__colour_id=colour_id)
        parent_category_id = None
        try:
            parent_category_id = int(request.GET.get('parent_category_id'))
        except:
            pass
        if parent_category_id is not None:
            products = products.filter(
                link__product__category__in=Category.objects.filter(parent_id=parent_category_id))
        category_id = None
        try:
            category_id = int(request.GET.get('category_id'))
        except:
            pass
        if category_id is not None:
            products = products.filter(link__product__category_id=category_id)
        order_by = ''
        try:
            order_by = str(request.GET.get('order_by', ''))
        except:
            pass
        if order_by != '':
            products = products.order_by(order_by)
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
            'objects': MainProductSerializer(products[(page - 1) * 16: page * 16], many=True).data
        }
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_products_item_view(request, id):
    if request.method == 'GET':
        try:
            product = OriginalProduct.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data=MainProductSerializer(product).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_colours_view(request):
    if request.method == 'GET':
        return Response(data=MainColourSerializer(IziColour.objects.all(), many=True).data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def client_sizes_view(request):
    if request.method == 'GET':
        return Response(data=IziSizeSerializer(Size.objects.all(), many=True).data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
