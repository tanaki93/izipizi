from django.db import transaction

# Create your views here.
from django.db import transaction
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from product_app.models import TrendYolCategory, Link, Brand, OriginalProduct, Document, NOT_PARSED, OUT_PROCESS, \
    PROCESSED, IN_PROCESS
# from projects_app.googletrans.client import Translator
from projects_app.admin_serializers import BrandAdminDetailedSerializer, DocumentSerializer
from user_app.models import User
from user_app.permissions import IsAdmin
from user_app.serializers import UserSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAdmin])
def admin_brands_list_view(request):
    if request.method == 'GET':
        brands = Brand.objects.all()
        return Response(data=BrandAdminDetailedSerializer(brands, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        user_id = int(request.data.get('user_id', 0))
        user = None
        try:
            user = User.objects.get(id=user_id)
        except:
            pass
        if user is None:
            return Response(data={'error': 'user not found'})
        else:
            categories = request.data.get('categories', [])
            # print(categories)
            document = Document()
            products = OriginalProduct.objects.filter(link__tr_category_id__in=categories, link__status=1)
            document.user = user
            document.save()
            document.original_products.add(*list(products))
            for i in products:
                i.link.status = 3
                i.link.save()
            document.save()
            return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAdmin])
def admin_users_list_view(request):
    if request.method == 'GET':
        role = 0
        try:
            role = int(request.GET.get('role', 0))
        except:
            pass
        if role == 0:
            users = User.objects.all()
        else:
            users = User.objects.filter(user_type=role)
        return Response(data=UserSerializer(users, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_statistics_view(request):
    if request.method == 'GET':
        links = Link.objects.all()
        data = {
            'not_parsed': links.filter(status=NOT_PARSED).count(),
            'out_process': links.filter(status=OUT_PROCESS).count(),
            'in_process': links.filter(status=IN_PROCESS).count(),
            'processed': links.filter(status=PROCESSED).count(),
            'all': links.count(),
        }
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_documents_view(request):
    if request.method == 'GET':
        documents = Document.objects.all()
        return Response(status=status.HTTP_200_OK, data=DocumentSerializer(documents, many=True).data)
