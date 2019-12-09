import datetime

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from product_app.models import Link, Brand, OriginalProduct, Document, NOT_PARSED, OUT_PROCESS, \
    PROCESSED, IN_PROCESS, Country, Currency, Language, ExchangeRate, VendDepartment, DocumentProduct, DocumentComment, \
    VendColour
from projects_app.admin_serializers import BrandAdminDetailedSerializer, DocumentSerializer, CurrencySerializer, \
    LanguageSerializer, ExchangeRateSerializer, CountrySerializer, DocumentDetailedSerializer
from projects_app.serializers import ProductSerializer, BrandProcessSerializer, VendColourSerializer, CommentSerializer
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
        brand = None
        try:
            brand = Brand.objects.get(id=int(request.data.get('brand_id')))
        except:
            pass
        with transaction.atomic():
            for i in VendDepartment.objects.filter(brand=brand):
                document = None
                try:
                    document = Document.objects.get(department=i, brand=brand)
                except:
                    pass
                if document is None:
                    document = Document.objects.create(department=i, brand=brand)
                    document.save()
                    products = OriginalProduct.objects.filter(department=i)
                    for j in products:
                        document_product = None
                        try:
                            document_product = DocumentProduct.objects.get(product=j)
                        except:
                            pass
                        if document_product is not None:
                            document_product.document = document
                            document_product.save()
                        else:
                            document_product = DocumentProduct.objects.create(product=j, document=document)
                            document_product.save()
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
        document_product = DocumentProduct.objects.all()
        data = {
            'not_parsed': 0,
            'out_process': document_product.filter(step=1).count(),
            'in_process': document_product.filter(step__in=[2, 3, 4]).count(),
            'processed': document_product.filter(step=5).count(),
            'all': document_product.count(),
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


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def admin_currencies_view(request):
    if request.method == 'GET':
        currencies = Currency.objects.all()
        return Response(data=CurrencySerializer(currencies, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        code = request.data.get('code', '')
        code_name = request.data.get('code_name', '')
        currency = Currency.objects.create(code=code, name=name, code_name=code_name)
        currency.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def admin_currencies_item_view(request, id):
    currencies = Currency.objects.get(id=id)
    if request.method == 'GET':
        return Response(data=CurrencySerializer(currencies).data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        currencies.name = request.data.get('name', '')
        currencies.code = request.data.get('code', '')
        currencies.code_name = request.data.get('code_name', '')
        currencies.is_active = request.data.get('is_active', True)
        # currency = Currency.objects.create(code=code, name=name)
        currencies.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        currencies.delete()
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
        if code != '':
            count = Language.objects.filter(code=code).count()
            if count > 0:
                return Response(status=status.HTTP_409_CONFLICT, data={'error': 'Данный код уже существует'})
        is_translate = request.data.get('is_translate', True)
        is_active = request.data.get('is_active', True)
        language = Language.objects.create(code=code, name=name, is_translate=is_translate, is_active=is_active)
        language.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def admin_languages_item_view(request, id):
    languages = Language.objects.get(id=id)
    if request.method == 'GET':
        return Response(data=LanguageSerializer(languages).data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        languages.name = request.data.get('name', '')
        languages.code = request.data.get('code', '')
        languages.is_translate = request.data.get('is_translate', True)
        languages.is_active = request.data.get('is_active', True)
        # currency = Currency.objects.create(code=code, name=name)
        languages.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        languages.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def admin_exchanges_view(request):
    if request.method == 'GET':
        exchanges = ExchangeRate.objects.all()
        return Response(data=ExchangeRateSerializer(exchanges, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        from_currency = None
        to_currency = None
        try:
            from_currency = int(request.data.get('from_currency_id'))
            to_currency = int(request.data.get('to_currency_id'))
        except:
            pass

        value = float(request.data.get('value', 0))
        is_active = request.data.get('is_active', True)
        if from_currency is not None and to_currency is not None:
            exchange = ExchangeRate.objects.create(from_currency_id=from_currency, to_currency_id=to_currency,
                                                   value=value, is_active=is_active)
            try:
                date = datetime.datetime.strptime(request.data.get('date'), "%Y-%m-%d")
                exchange.date = date
            except:
                pass
            exchange.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def admin_exchanges_item_view(request, id):
    exchange = ExchangeRate.objects.get(id=id)
    if request.method == 'GET':
        return Response(data=ExchangeRateSerializer(exchange).data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        from_currency = None
        to_currency = None
        try:
            from_currency = int(request.data.get('from_currency_id'))
            to_currency = int(request.data.get('to_currency_id'))
        except:
            pass
        value = float(request.data.get('value', 0))
        is_active = request.data.get('is_active', True)
        if from_currency is not None and to_currency is not None:
            exchange.to_currency_id = to_currency
            exchange.from_currency_id = from_currency
            exchange.value = value
            try:
                date = datetime.datetime.strptime(request.data.get('date'), "%Y-%m-%d")
                exchange.date = date
            except:
                pass
            exchange.is_active = is_active
            exchange.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    elif request.method == 'DELETE':
        exchange.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def admin_countries_view(request):
    if request.method == 'GET':
        countries = Country.objects.all()
        return Response(data=CountrySerializer(countries, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        language = None
        currency = None
        try:
            language = int(request.data.get('language_id'))
            currency = int(request.data.get('currency_id'))
        except:
            pass
        code = str(request.data.get('code', ''))
        name = str(request.data.get('name', ''))
        is_active = request.data.get('is_active', True)
        if language is not None and currency is not None:
            exchange = Country.objects.create(language_id=language, currency_id=currency, name=name, code=code, is_active=is_active)
            exchange.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def admin_countries_item_view(request, id):
    country = Country.objects.get(id=id)
    if request.method == 'GET':
        return Response(data=CountrySerializer(country).data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        language = None
        currency = None
        try:
            language = int(request.data.get('language_id'))
            currency = int(request.data.get('currency_id'))
        except:
            pass
        code = str(request.data.get('code', ''))
        name = str(request.data.get('name', ''))
        is_active = request.data.get('is_active', True)
        if language is not None and currency is not None:
            country.language_id = language
            country.currency_id = currency
            country.code = code
            country.name = name
            country.is_active = is_active
            country.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    elif request.method == 'DELETE':
        country.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT','POST'])
@permission_classes([AllowAny])
def admin_documents_item_view(request, id):
    try:
        document = Document.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        department = None
        try:
            department = document.department
        except:
            pass
        data = {
            'step': document.step,
            'id': document.id,
        }
        if department is None:
            data['department_id'] = None
            data['department_name'] = None
        else:
            data['department_id'] = document.department.id
            data['department_name'] = document.department.name
        data['brand'] = BrandProcessSerializer(document.brand).data
        data['colours'] = VendColourSerializer(VendColour.objects.all(), many=True).data
        data['comments'] = CommentSerializer(DocumentComment.objects.filter(document=document), many=True).data
        return Response(status=status.HTTP_200_OK, data=data)
    elif request.method == 'PUT':
        comment = request.data.get('comment', '')
        document_comment = DocumentComment.objects.create(document=document, text=comment)
        document_comment.save()
        document.step = 1
        document.save()
        with transaction.atomic():
            for i in DocumentProduct.objects.filter(document=document):
                i.step = 1
                i.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'POST':
        document.step = 5
        document.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_documents_process_products_view(request, id):
    try:
        document = Document.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        query = request.GET.get('query', '')
        data = {}
        products = OriginalProduct.objects.filter(originalproduct__document_id=id, originalproduct__step=document.step)
        if query != "":
            products = products.filter(title_lower__contains=query)
        department_id = None
        try:
            department_id = int(request.GET.get('department_id', ''))
        except:
            pass
        if department_id is not None:
            products = products.filter(department_id=department_id)
        category_id = None
        try:
            category_id = int(request.GET.get('category_id', ''))
        except:
            pass
        if category_id is not None:
            products = products.filter(category_id=category_id)
        colour_id = None
        try:
            colour_id = int(request.GET.get('colour_id', ''))
        except:
            pass
        if colour_id is not None:
            products = products.filter(colour_id=colour_id)
        length = products.count()
        pages = length // 200
        if pages == 0:
            pages = 1
        elif length % 200 != 0:
            pages += 1
        data['count'] = length
        data['pages'] = pages
        data['products'] = ProductSerializer(products[:200], many=True).data
        return Response(status=status.HTTP_200_OK, data=data)
