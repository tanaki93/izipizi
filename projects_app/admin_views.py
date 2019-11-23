from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from product_app.models import Link, Brand, OriginalProduct, Document, NOT_PARSED, OUT_PROCESS, \
    PROCESSED, IN_PROCESS, Country, Currency, Language
from projects_app.admin_serializers import BrandAdminDetailedSerializer, DocumentSerializer, CurrencySerializer, \
    LanguageSerializer
from projects_app.serializers import ProductSerializer
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
    elif request.method == 'POST':
        username = request.data['username']
        password = request.data['password']
        user = User.objects.create_user(username=username, email='', password=password)
        try:
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            user.first_name = first_name
            user.last_name = last_name
        except:
            pass
        user.email = request.data.get('email', 't@m.ru')
        user.phone = request.data.get('phone', '+996 700 121212')
        user.user_type = int(request.data.get('user_type', 2))
        user.save()
        return Response(status=status.HTTP_201_CREATED)


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


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_products_view(request):
    if request.method == 'GET':
        page = 1
        try:
            page = int(request.GET.get('page', '1'))
        except:
            pass
        products = OriginalProduct.objects.all()
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


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_countries_view(request):
    if request.method == 'GET':
        countries = Country.objects.all()
    return None


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def admin_currencies_view(request):
    if request.method == 'GET':
        currencies = Currency.objects.all()
        return Response(data=CurrencySerializer(currencies, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        code = request.data.get('code', '')
        currency = Currency.objects.create(code=code, name=name)
        currency.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def admin_currencies_item_view(request, id):
    currencies = Currency.objects.get(id=id)
    if request.method == 'GET':
        return Response(data=CurrencySerializer(currencies).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        currencies.name = request.data.get('name', '')
        currencies.code = request.data.get('code', '')
        # currency = Currency.objects.create(code=code, name=name)
        currencies.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def admin_languages_view(request):
    if request.method == 'GET':
        languages = Language.objects.all()
        return Response(data=LanguageSerializer(languages, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        code = request.data.get('code', '')
        is_translate = request.data.get('is_translate', True)
        language = Language.objects.create(code=code, name=name, is_translate=is_translate)
        language.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def admin_languages_item_view(request, id):
    languages = Language.objects.get(id=id)
    if request.method == 'GET':
        return Response(data=LanguageSerializer(languages).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        languages.name = request.data.get('name', '')
        languages.code = request.data.get('code', '')
        languages.is_translate = request.data.get('is_translate', True)
        # currency = Currency.objects.create(code=code, name=name)
        languages.save()
        return Response(status=status.HTTP_200_OK)