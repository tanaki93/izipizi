from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from projects_app.models import Brand
from projects_app.serializers import BrandSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def brands_list_view(request):
    if request.method == 'GET':
        brands = Brand.objects.filter(is_active=True)
        return Response(data=BrandSerializer(brands, many=True).data)
