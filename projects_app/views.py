from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from projects_app.models import Brand, TrendYolDepartment, TrendYolCategory
from projects_app.serializers import BrandSerializer


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
                            category = TrendYolCategory.objects.get(name=k['name'], link=k['link'], department=department)
                        except:
                            pass
                        if category is None:
                            category = TrendYolCategory()
                            category.name = k['name']
                            category.link = k['link']
                            category.department = department
                            category.save()

        return Response(status=status.HTTP_200_OK)
