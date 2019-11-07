from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from product_app.models import Brand, TrendYolDepartment, TrendYolCategory, Department, Category, TrendyolSize, Size, \
    Link
from projects_app.serializers import BrandSerializer, BrandDetailedSerializer, TrendYolDepartmentSerializer, \
    TrendYolDepartmentDetailedSerializer, DepartmentSerializer, TrendYolCategorySerializer, \
    TrendYolCategoryDetailedSerializer, CategorySerializer
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
        categories = TrendYolCategory.objects.filter(is_active=True, department__brand__is_active=True, department__is_active=True, department__brand__is_trend_yol=True)
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
@permission_classes([IsOperator])
def operator_brands_list_view(request):
    if request.method == 'GET':
        brands = Brand.objects.all()
        return Response(data=BrandSerializer(brands, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        if name == '':
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        brand = Brand.objects.create(name=name, is_active=True)
        brand.save()
        return Response(status=status.HTTP_200_OK, data=BrandSerializer(brand).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsOperator])
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
        name = request.data.get('name', '')
        brand.is_active = is_active
        brand.name = name
        brand.save()
        return Response(status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def operator_departments_list_view(request, id):
#     if request.method == 'GET':
#         brand = Brand.objects.get(id=id)
#         departments = TrendYolDepartment.objects.filter(brand=brand)
#         return Response(data=TrendYolDepartmentDetailedSerializer(departments, many=True).data,
#                         status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsOperator])
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
            depart.code = request.data.get('code', '')
            depart.name = request.data.get('name', '')
            depart.save()
        else:
            depart = Department.objects.get(id=department_id)
        department.department = depart
        department.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsOperator])
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
            depart.code = request.data.get('code', '')
            depart.name = request.data.get('name', '')
            depart.save()
        else:
            depart = Department.objects.get(id=category_id)
        category.category = depart
        category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsOperator])
def operator_departments_search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        departments = Department.objects.filter(name_lower__contains=query.lower())
        return Response(status=status.HTTP_200_OK, data=DepartmentSerializer(departments, many=True).data)


@api_view(['GET'])
@permission_classes([IsOperator])
def operator_category_search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        categories = Category.objects.filter(name_lower__contains=query.lower())
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(categories, many=True).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsOperator])
def operator_category_item_view(request, id):
    category = Category.objects.get(id=id)
    if request.method == 'PUT':
        category.code = request.data.get('code', '')
        category.name = request.data.get('name', '')
        category.save()
    return Response(status=status.HTTP_200_OK, data=CategorySerializer(category).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsOperator])
def operator_department_item_view(request, id):
    deparment = Department.objects.get(id=id)
    if request.method == 'PUT':
        deparment.code = request.data.get('code', '')
        deparment.name = request.data.get('name', '')
        deparment.save()
    return Response(status=status.HTTP_200_OK, data=DepartmentSerializer(deparment).data)


def categories_zara_list_view(request):
    return None