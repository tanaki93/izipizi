from pprint import pprint

from bs4 import BeautifulSoup
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from product_app.models import Brand, TrendYolDepartment, TrendYolCategory, Department, Category, TrendyolSize, Size, \
    Link, OriginalProduct, Variant, Product, Document, ParentCategory
# from projects_app.googletrans.client import Translator
from product_app.serializers import ParentCategorySerializer
from projects_app.admin_serializers import DocumentSerializer, DocumentDetailedSerializer
from projects_app.googletrans import Translator
from projects_app.serializers import BrandSerializer, BrandDetailedSerializer, TrendYolDepartmentSerializer, \
    TrendYolDepartmentDetailedSerializer, DepartmentSerializer, TrendYolCategorySerializer, \
    TrendYolCategoryDetailedSerializer, CategorySerializer, LinkSerializer, ProductSerializer
from user_app.permissions import IsOperator


def save_size(tr_size):
    size = None
    try:
        size = Size.objects.get(trendyol_size=tr_size)
    except:
        pass
    if size is None:
        name = tr_size.name
        name_data = name.split()
        if name == 'TEK EBAT':
            name = 'один размер'
        elif len(name_data) > 1:
            data = name_data[1]
            if data == 'AY':
                name = name_data[0] + ' мес.'
            if data == 'YAŞ':
                name = name_data[0] + ' год'
        size = Size.objects.create(trendyol_size=tr_size, name=name)
        size.save()


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def categories_list_view(request):
    if request.method == 'GET':
        categories = TrendYolCategory.objects.filter(is_active=True, department__brand__is_active=True,
                                                     department__is_active=True, department__brand__is_trend_yol=True)
        return Response(data=TrendYolCategoryDetailedSerializer(categories, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        with transaction.atomic():
            for i in request.data:
                category = TrendYolCategory.objects.get(id=int(i['category_id']))
                for j in i['links']:
                    link = None
                    try:
                        link = Link.objects.get(url=j, tr_category_id=category.id)
                    except:
                        pass
                    if link is None:
                        link = Link.objects.create(url=j, tr_category=category)
                        link.save()
        return Response(status=status.HTTP_200_OK)


def translate_text(text):
    data = ''
    try:
        translator = Translator(service_urls=['translate.google.com.tr'])
        data = u'' + translator.translate(text, dest='ru').text
    except:
        pass
    return data


def create_original_product(link, param):
    original_product = OriginalProduct()
    original_product.link = link
    original_product.product_code = param['productCode']
    original_product.title = param['name']
    original_product.colour = param['color']
    original_product.product_id = param['id']
    original_product.discount_price = param['price']['discountedPrice']['value']
    original_product.original_price = param['price']['originalPrice']['value']
    original_product.selling_price = param['price']['sellingPrice']['value']
    try:
        original_product.is_rush_delivery = param['deliveryInformation']['isRushDelivery']
    except:
        pass
    try:
        original_product.delivery_date = param['deliveryInformation']['deliveryDate']
    except:
        pass
    original_product.is_free_argo = param['isFreeCargo']
    images = ''
    for image in param['images']:
        images += ('https://img-trendyol.mncdn.com/' + image + ' ')
    original_product.images = images.strip()
    promotions = ''
    for promotion in param['promotions']:
        promotions += (promotion['text'] + '|\n')
    original_product.promotions = promotions
    original_product.description = param['description']
    original_product.save()
    for variant in param['variants']:
        variant_item = Variant()
        tr_size = None
        try:
            tr_size = TrendyolSize.objects.get(name=variant['attributeValue'].upper())
        except:
            pass
        if tr_size is None:
            tr_size = TrendyolSize.objects.create(name=variant['attributeValue'].upper())
            tr_size.save()
        save_size(tr_size)
        variant_item.tr_size = tr_size
        variant_item.original_product = original_product
        if variant['stock'] != 0:
            variant_item.stock = True
        else:
            variant_item.stock = False
        variant_item.save()
    product = Product()
    product.link = link
    product.title = translate_text(param['name'])
    product.colour = translate_text(param['color'])
    ul_soup = BeautifulSoup(param['description'], 'lxml')
    description = ''
    try:
        product.brand_id = original_product.link.tr_category.department.brand_id
        product.department_id = original_product.link.tr_category.department.department_id
        product.category_id = original_product.link.tr_category.category_id
    except:
        pass
    for i in (ul_soup.find_all('li')):
        description += (i.text + '| ')
    product.description = translate_text(description)
    product.save()

    link.status = 1
    link.save()


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def links_trendyol_list_view(request):
    if request.method == 'GET':
        links = Link.objects.filter(tr_category__isnull=False, tr_category__is_active=True,
                                    tr_category__department__brand__is_trend_yol=True, originalproduct__isnull=True)
        # print(links)
        return Response(data=LinkSerializer(links, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        with transaction.atomic():
            for i in request.data:
                link = None
                try:
                    link = Link.objects.get(id=int(i['id']))
                except:
                    pass
                if link is None:
                    continue
                original_product = None
                try:
                    original_product = link.originalproduct
                except:
                    pass
                if original_product is None:
                    create_original_product(link, i['product'])
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def brands_list_view(request):
    if request.method == 'GET':
        brands = Brand.objects.filter(is_active=True, is_trend_yol=True)
        return Response(data=BrandSerializer(brands, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        for i in request.data:
            brand = Brand.objects.get(id=i['id'])
            with transaction.atomic():
                for size in i['sizes']:
                    tr_size = None
                    try:
                        tr_size = TrendyolSize.objects.get(name=size.upper())
                    except:
                        pass
                    if tr_size is None:
                        tr_size = TrendyolSize.objects.create(name=size.upper())
                        tr_size.save()
                    save_size(tr_size)
            with transaction.atomic():
                for j in i['departments']:
                    department = None
                    try:
                        department = TrendYolDepartment.objects.get(name=j['name'], link=j['link'], brand=brand)
                    except:
                        pass
                    if department is None:
                        department = TrendYolDepartment()
                        department.name = j['name']
                        department.link = j['link']
                        department.brand = brand
                        department.save()
                    for k in j['categories']:
                        category = None
                        try:
                            category = TrendYolCategory.objects.get(name=k['name'], link=k['link'],
                                                                    department=department)
                        except:
                            pass
                        if category is None:
                            category = TrendYolCategory()
                            category.name = k['name']
                            category.link = k['link']
                            category.department = department
                            category.save()

        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_brands_list_view(request):
    if request.method == 'GET':
        brands = Brand.objects.all()
        return Response(data=BrandSerializer(brands, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        is_active = request.data.get('is_active', True)
        is_trend_yol = request.data.get('is_trend_yol', True)
        name = request.data.get('name', '')
        link = request.data.get('link', '')
        if name == '':
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        brand = Brand.objects.create(name=name, is_active=is_active, is_trend_yol=is_trend_yol, link=link)
        brand.save()
        return Response(status=status.HTTP_200_OK, data=BrandSerializer(brand).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_brands_item_view(request, id):
    brand = None
    try:
        brand = Brand.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(data=BrandDetailedSerializer(brand).data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        is_active = request.data.get('is_active', True)
        is_trend_yol = request.data.get('is_trend_yol', True)
        name = request.data.get('name', '')
        link = request.data.get('link', '')
        brand.is_active = is_active
        brand.name = name
        brand.link = link
        brand.is_trend_yol = is_trend_yol
        brand.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def operator_brands_refresh_item_view(request, id):
    brand = None
    try:
        brand = Brand.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        brand.save()
        return Response(data=BrandSerializer(brand).data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def operator_departments_list_view(request, id):
#     if request.method == 'GET':
#         brand = Brand.objects.get(id=id)
#         departments = TrendYolDepartment.objects.filter(brand=brand)
#         return Response(data=TrendYolDepartmentDetailedSerializer(departments, many=True).data,
#                         status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_departments_item_view(request, id):
    department = None
    try:
        department = TrendYolDepartment.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(data=TrendYolDepartmentDetailedSerializer(department).data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        is_active = request.data.get('is_active', True)
        department.is_active = is_active
        department.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'POST':
        department_id = int(request.data.get('department_id', 0))
        if department_id == 0:
            depart = Department()
            # depart.code = request.data.get('code', '')
            depart.name = request.data.get('name', '')
            depart.save()
        else:
            depart = Department.objects.get(id=department_id)
        department.department = depart
        department.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_categories_item_view(request, id):
    category = None
    try:
        category = TrendYolCategory.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(data=TrendYolCategoryDetailedSerializer(category).data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        is_active = request.data.get('is_active', True)
        category.is_active = is_active
        category.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'POST':
        category_id = int(request.data.get('category_id', 0))
        if category_id == 0:
            depart = Category()
            # depart.code = request.data.get('code', '')
            depart.name = request.data.get('name', '')
            depart.save()
        else:
            depart = Category.objects.get(id=category_id)
        category.category = depart
        category.save()
        categories = TrendYolCategory.objects.filter(name=category.name, category__isnull=True)
        for i in categories:
            i.category.name = category.category.name
            i.category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_departments_search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        departments = Department.objects.filter(name_lower__contains=query.lower())
        return Response(status=status.HTTP_200_OK, data=DepartmentSerializer(departments, many=True).data)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        category = Department()
        category.name = name
        category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_category_search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        categories = Category.objects.filter(name_lower__contains=query.lower())
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(categories, many=True).data)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        category = Category()
        category.name = name
        category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_parent_category_search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        categories = ParentCategory.objects.filter(name_lower__contains=query.lower())
        return Response(status=status.HTTP_200_OK, data=ParentCategorySerializer(categories, many=True).data)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        category = ParentCategory()
        category.name = name
        category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_category_item_view(request, id):
    category = Category.objects.get(id=id)
    if request.method == 'PUT':
        # category.code = request.data.get('code', '')
        category.name = request.data.get('name', '')
        try:
            category.parent_id = int(request.data.get('parent_id', ''))
        except:
            pass
        category.save()
    return Response(status=status.HTTP_200_OK, data=CategorySerializer(category).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_parent_category_item_view(request, id):
    category = ParentCategory.objects.get(id=id)
    if request.method == 'PUT':
        # category.code = request.data.get('code', '')
        category.name = request.data.get('name', '')
        category.save()
    return Response(status=status.HTTP_200_OK, data=ParentCategorySerializer(category).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_department_item_view(request, id):
    deparment = Department.objects.get(id=id)
    if request.method == 'PUT':
        # deparment.code = request.data.get('code', '')
        deparment.name = request.data.get('name', '')
        deparment.save()
    return Response(status=status.HTTP_200_OK, data=DepartmentSerializer(deparment).data)


def categories_zara_list_view(request):
    return None


@api_view(['GET'])
@permission_classes([IsOperator])
def operator_documents_view(request):
    if request.method == 'GET':
        documents = Document.objects.filter(user=request.user)
        return Response(status=status.HTTP_200_OK, data=DocumentSerializer(documents, many=True).data)


@api_view(['GET'])
@permission_classes([IsOperator])
def operator_documents_item_view(request, id):
    try:
        document = Document.objects.get(id=id, user=request.user)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(status=status.HTTP_200_OK, data=DocumentDetailedSerializer(document).data)


@api_view(['GET'])
@permission_classes([IsOperator])
def operator_documents_products_view(request, id):
    try:
        document = Document.objects.get(id=id, user=request.user)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        page = 1
        try:
            page = int(request.GET.get('page', '1'))
        except:
            pass
        products = document.original_products.all()
        category_id = None
        try:
            category_id = int(request.GET.get('category_id'))
        except:
            pass
        if category_id is not None:
            products = products.filter(link__tr_category_id=category_id)
        pages = products.count() // 10
        if products.count() % 10 != 0:
            pages += 1
        data = {
            'pages': pages,
            'page': page,
            'count': products.count(),
            'objects': ProductSerializer(products[(page - 1) * 10: page * 10], many=True).data
        }
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET', 'PUT'])
@permission_classes([IsOperator])
def operator_documents_products_item_view(request, document_id, id):
    try:
        document = Document.objects.get(id=document_id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        product = OriginalProduct.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    products = document.original_products.filter(id=product.id).first()
    if request.method == 'GET':
        return Response(status=status.HTTP_200_OK, data=ProductSerializer(products).data)
    elif request.method == 'PUT':
        # print(request.data)
        product = Product.objects.get(link=products.link)
        product.title = request.data.get('title', '')
        product.description = request.data.get('description', '')
        product.colour = request.data.get('colour', '')
        product.selling_price = request.data.get('selling_price', '')
        product.discount_price = request.data.get('discount_price', '')
        product.original_price = request.data.get('original_price', '')
        try:
            product.department_id = int(request.data.get('department_id', ''))
        except:
            pass
        try:
            product.category_id = int(request.data.get('category_id', ''))
        except:
            pass
        product.save()
        status_data = None
        try:
            status_data = int(request.data.get('status', '2'))
        except:
            pass
        product.link.status = status_data
        product.link.save()
        return Response(status=status.HTTP_200_OK)
