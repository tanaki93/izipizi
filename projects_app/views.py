from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from product_app.models import Brand, TrendYolDepartment, TrendYolCategory, Department, Category
from projects_app.serializers import BrandSerializer, BrandDetailedSerializer, TrendYolDepartmentSerializer, \
    TrendYolDepartmentDetailedSerializer, DepartmentSerializer, TrendYolCategorySerializer, \
    TrendYolCategoryDetailedSerializer, CategorySerializer
from user_app.permissions import IsOperator


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def brands_list_view(request):
    if request.method == 'GET':
        brands = Brand.objects.filter(is_active=True)
        return Response(data=BrandSerializer(brands, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        for i in request.data:
            brand = Brand.objects.get(id=i['id'])
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
        brand.is_active = is_active
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

