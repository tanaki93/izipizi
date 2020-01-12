from pprint import pprint
from django.db.models import Q
from bs4 import BeautifulSoup
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from product_app.models import Brand, VendDepartment, VendCategory, Department, Category, VendSize, Size, \
    Link, OriginalProduct, Variant, Product, Document, ParentCategory, BrandCountry, Language, TranslationDepartment, \
    TranslationCategory, VendColour, TranslationColour, DocumentProduct, DocumentComment, TranslationParentCategory, \
    IziColour, TranslationSize, Content, TranslationContent
from product_app.serializers import ParentCategorySerializer
from projects_app.admin_serializers import DocumentSerializer, DocumentDetailedSerializer
from projects_app.googletrans import Translator
from projects_app.serializers import BrandSerializer, BrandDetailedSerializer, TrendYolDepartmentSerializer, \
    TrendYolDepartmentDetailedSerializer, DepartmentSerializer, TrendYolCategorySerializer, \
    TrendYolCategoryDetailedSerializer, CategorySerializer, LinkSerializer, ProductSerializer, VendSizeSerializer, \
    VendColourSerializer, BrandProcessSerializer, CommentSerializer, ColourSerializer, ColourSerializer, \
    IziColorSerializer, IziColourSerializer, SizeSerializer, ContentSerializer, IziShopProductSerializer
from user_app.permissions import IsOperator


def save_size(tr_size):
    size = None
    try:
        size = Size.objects.get(vend_size=tr_size)
    except:
        pass
    if size is None:
        name = tr_size.name
        name_data = name.split()
        if name == 'TEK EBAT':
            name = 'one size'
        elif len(name_data) > 1:
            data = name_data[1]
            if data == 'AY':
                name = name_data[0] + ' month'
            if data == 'YAŞ':
                name = name_data[0] + ' year'
        size = Size.objects.create(vend_size=tr_size, name=name)
        size.save()


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def categories_list_view(request):
    if request.method == 'GET':
        brand = request.GET.get('brand', '')
        categories = []
        if brand == '':
            categories = VendCategory.objects.filter(is_active=True, department__brand__is_active=True,
                                                     department__is_active=True)
        elif brand == 'zara':
            categories = VendCategory.objects.filter(is_active=True, department__brand__is_active=True,
                                                     department__is_active=True,
                                                     department__brand__link='https://www.zara.com/tr/')
        elif brand == 'handm':
            categories = VendCategory.objects.filter(is_active=True, department__brand__is_active=True,
                                                     department__is_active=True,
                                                     department__brand__link='https://www2.hm.com/tr_tr/')
        return Response(data=TrendYolCategoryDetailedSerializer(categories, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        with transaction.atomic():
            for i in request.data:
                category = VendCategory.objects.get(id=int(i['category_id']))
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


def translate_text(text, dest='ru'):
    data = ''
    try:
        translator = Translator(service_urls=['translate.google.com.tr'])
        data = u'' + translator.translate(text, dest=dest).text
    except:
        pass
    return data


def create_zara_product(link, param):
    original_product = OriginalProduct()
    original_product.link = link
    original_product.product_code = None
    original_product.title = param['name']
    original_product.product_id = link.url
    original_product.discount_price = param['selling_price']
    original_product.selling_price = param['selling_price']
    original_product.original_price = param['selling_price']
    colour = param['colour']
    original_product.colour_code = colour
    images = ''
    for image in param['images']:
        images += (image + ' ')
    original_product.images = images.strip()
    original_product.description = param['description']

    vend_colour = None
    try:
        vend_colour = VendColour.objects.get(name=colour)
    except:
        pass
    if vend_colour is None:
        vend_colour = VendColour.objects.create(name=colour)
        vend_colour.save()
    original_product.colour = vend_colour
    original_product.save()
    for variant in param['sizes']:
        variant_item = Variant()
        tr_size = None
        try:
            tr_size = VendSize.objects.get(name=variant['value'].upper())
        except:
            pass
        if tr_size is None:
            tr_size = VendSize.objects.create(name=variant['value'].upper())
            tr_size.save()
        # save_size(tr_size)
        variant_item.tr_size = tr_size
        variant_item.original_product = original_product
        variant_item.stock = variant['stock']
        variant_item.save()
    try:
        original_product.brand_id = original_product.link.tr_category.department.brand_id
    except:
        pass
    try:
        original_product.department_id = original_product.link.tr_category.department_id
    except:
        pass
    try:
        original_product.category_id = original_product.link.tr_category_id
    except:
        pass
    original_product.save()
    product = Product()
    product.link = link
    try:
        product.department_id = original_product.link.tr_category.department.department_id
    except:
        pass
    try:
        product.category_id = original_product.link.tr_category.category_id
    except:
        pass
    try:
        product.colour_id = original_product.colour.izi_colour.id
    except:
        pass
    product.save()
    product_document = DocumentProduct.objects.create(product=original_product)
    product_document.save()


def create_original_product(link, param):
    original_product = OriginalProduct()
    original_product.link = link
    original_product.product_code = param['productCode']
    original_product.title = param['name']
    for i in param['attributes']:
        if i['key']['name'] == 'Renk':
            colour = i['value']['name']
            vend = VendColour.objects.filter(name=colour)
            if len(vend) > 0:
                original_product.colour = vend.first()
            break
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
        images += ('https://trendyol.com' + image + ' ')
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
            tr_size = VendSize.objects.get(name=variant['attributeValue'].upper())
        except:
            pass
        if tr_size is None:
            tr_size = VendSize.objects.create(name=variant['attributeValue'].upper())
            tr_size.save()
        # save_size(tr_size)
        variant_item.tr_size = tr_size
        variant_item.original_product = original_product
        if variant['stock'] != 0:
            variant_item.stock = True
        else:
            variant_item.stock = False
        variant_item.save()
    try:
        original_product.brand_id = original_product.link.tr_category.department.brand_id
    except:
        pass
    try:
        original_product.department_id = original_product.link.tr_category.department_id
    except:
        pass
    try:
        original_product.category_id = original_product.link.tr_category_id
    except:
        pass
    original_product.save()
    product = Product()
    product.link = link
    try:
        product.department_id = original_product.link.tr_category.department.department_id
    except:
        pass
    try:
        product.category_id = original_product.link.tr_category.category_id
    except:
        pass
    try:
        product.colour_id = original_product.colour.izi_colour.id
    except:
        pass
    product.save()
    product_document = DocumentProduct.objects.create(product=original_product)
    product_document.save()


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def links_brand_list_view(request):
    if request.method == 'GET':
        brand = request.GET.get('brand', '')
        links = []
        if brand == 'zara':
            links = Link.objects.filter(tr_category__isnull=False, tr_category__is_active=True,
                                        tr_category__department__is_active=True,
                                        originalproduct__isnull=True,
                                        tr_category__department__brand__link='https://www.zara.com/tr/')
        elif brand == 'handm':
            links = Link.objects.filter(tr_category__isnull=False, tr_category__is_active=True,
                                        tr_category__department__is_active=True,
                                        originalproduct__isnull=True,
                                        tr_category__department__brand__link='https://www2.hm.com/tr_tr/')

        return Response(data=LinkSerializer(links, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        with transaction.atomic():
            brand = request.GET.get('brand', '')
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
                if original_product is None and brand == 'zara':
                    create_zara_product(link, i['product'])
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def links_trendyol_list_view(request):
    if request.method == 'GET':
        links = Link.objects.filter(tr_category__isnull=False, tr_category__is_active=True,
                                    tr_category__department__is_active=True,
                                    originalproduct__isnull=True)
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
                print(original_product)
                if original_product is None:
                    create_original_product(link, i['product'])

        return Response(status=status.HTTP_200_OK)


def colour_original_product(link, param):
    original_product = link.originalproduct
    original_product.colour_code = param['color']
    original_product.save()
    colour = str(param['color']).split('/')[0].lower()
    vend = VendColour.objects.filter(name_lower=colour)
    if len(vend) > 0:
        original_product.colour = vend.first()
        original_product.save()
        try:
            product = link.product
            product.colour = original_product.colour.izi_colour
            product.save()
        except:
            pass
    # else:
    #     vend = VendColour.objects.create(name=original_product.colour_code)
    #     vend.save()
    #     original_product.colour = vend
    #     original_product.save()


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def links_colour_list_view(request):
    if request.method == 'GET':
        # page = int(request.GET.get('page',1))
        links = Link.objects.filter(originalproduct__isnull=False, originalproduct__colour__isnull=True)
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
                colour_original_product(link, i['product'])
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([AllowAny])
def brands_list_view(request):
    if request.method == 'GET':
        brand = request.GET.get('brand', '')
        if brand == '':
            brands = Brand.objects.filter(is_active=True)
            return Response(data=BrandSerializer(brands, many=True).data, status=status.HTTP_200_OK)
        elif brand == 'Collins':
            brands = Brand.objects.get(link='https://www.colins.com.tr/')
            return Response(data=BrandSerializer(brands).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        for i in request.data:
            brand = Brand.objects.get(id=i['id'])
            with transaction.atomic():
                for size in i['sizes']:
                    tr_size = None
                    try:
                        tr_size = VendSize.objects.get(name=size.upper())
                    except:
                        pass
                    if tr_size is None:
                        tr_size = VendSize.objects.create(name=size.upper())
                        tr_size.save()
                    save_size(tr_size)
            languages = Language.objects.all()
            with transaction.atomic():
                for c in i['colours']:
                    vend_colour = None
                    try:
                        vend_colour = VendColour.objects.get(name=c)
                    except:
                        pass
                    if vend_colour is None:
                        vend_colour = VendColour.objects.create(name=c, name_en=translate_text(c, 'en'))
                        vend_colour.save()
                        for language in languages:
                            colour = TranslationColour.objects.create(name=translate_text(c, language.code),
                                                                      language=language, vend_colour=vend_colour)
                            colour.save()
            with transaction.atomic():
                for j in i['departments']:
                    department = None
                    try:
                        department = VendDepartment.objects.get(name=j['name'], link=j['link'], brand=brand)
                    except:
                        pass
                    if department is None:
                        deps = VendDepartment.objects.filter(name=j['name'])
                        department = VendDepartment()
                        department.name = j['name']
                        department.link = j['link']
                        department.brand = brand
                        department.save()
                        flag = True
                        if len(deps) > 0:
                            dep = deps.first()
                            if dep.department is not None:
                                department.department = dep.department
                                department.save()
                                flag = False
                        if flag:
                            name = translate_text(j['name'], 'en')
                            new_dep = None
                            try:
                                new_dep = Department.objects.get(name=name)
                            except:
                                pass
                            if new_dep is None:
                                new_dep = Department.objects.create(name=name)
                                new_dep.save()
                                for i in languages:
                                    translation_dep = TranslationDepartment.objects.create(department=new_dep,
                                                                                           name=translate_text(
                                                                                               j['name'],
                                                                                               i.code).capitalize(),
                                                                                           language=i)
                                    translation_dep.save()
                            department.department = new_dep
                            department.save()
                    for k in j['categories']:
                        category = None
                        try:
                            category = VendCategory.objects.get(name=k['name'], link=k['link'],
                                                                department=department)
                        except:
                            pass
                        if category is None:
                            # cats = VendCategory.objects.filter(name=k['name'])
                            category = VendCategory()
                            category.name = k['name']
                            category.link = k['link']
                            category.department = department
                            category.save()
                            # flag = True
                            # if len(cats) > 0:
                            #     cat = cats.first()
                            #     if cat.category is not None:
                            #         category.category = cat.category
                            #         category.save()
                            #         flag = False
                            # if flag:
                            #     name = translate_text(k['name'], 'en')
                            #     new_dep = None
                            #     try:
                            #         new_dep = Category.objects.get(name=name)
                            #     except:
                            #         pass
                            #     if new_dep is None:
                            #         new_dep = Category.objects.create(name=name)
                            #         new_dep.save()
                            #         for i in languages:
                            #             translation_dep = TranslationCategory.objects.create(category=new_dep,
                            #                                                                  name=translate_text(
                            #                                                                      k['name'],
                            #                                                                      i.code).capitalize(),
                            #                                                                  language=i)
                            #             translation_dep.save()
                            #     category.category = new_dep
                            #     category.save()
        return Response(status=status.HTTP_200_OK)
    if request.method == 'PUT':
        brand = request.GET.get('brand', '')
        if brand == 'Collins':
            new_brand = None
            try:
                new_brand = Brand.objects.get(name='Collins')
            except:
                pass
            if new_brand is not None:
                for i in request.data:
                    department_name = i['department']
                    department = None
                    try:
                        department = VendDepartment.objects.get(brand=new_brand, name=department_name)
                    except:
                        pass
                    if department is None:
                        department = VendDepartment.objects.create(brand=new_brand, name=department_name)
                        department.save()
                        for j in i['categories']:
                            category_name = j['category']
                            category_link = j['link']
                            category = None
                            try:
                                category = VendCategory.objects.get(department=department, name=category_name,
                                                                    link=category_link)
                            except:
                                pass
                            if category is None:
                                category = VendCategory.objects.create(department=department, name=category_name,
                                                                       link=category_link)
                                category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def operator_brands_list_view(request):
    if request.method == 'GET':
        brands = Brand.objects.all()
        return Response(data=BrandSerializer(brands, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        is_active = request.data.get('is_active', True)
        # is_trend_yol = request.data.get('is_trend_yol', True)
        name = request.data.get('name', '')
        link = request.data.get('link', '')
        code = request.data.get('code', '').upper()
        currency_id = int(request.data.get('currency_id', ''))
        if name == '':
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        brand = Brand.objects.create(name=name, is_active=is_active, link=link, code=code, currency_id=currency_id)
        brand.save()
        countries = request.data.get('countries')
        for i in countries:
            brand_country = BrandCountry()
            brand_country.brand = brand
            brand_country.country_id = i['country_id']
            brand_country.mark_up = i['mark_up']
            brand_country.round_digit = i['round_digit']
            brand_country.round_to = i['round_to']
            brand_country.save()
        return Response(status=status.HTTP_200_OK, data=BrandSerializer(brand).data)


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
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
        # is_trend_yol = request.data.get('is_trend_yol', True)
        name = request.data.get('name', '')
        link = request.data.get('link', '')
        code = request.data.get('code', '').upper()
        currency_id = int(request.data.get('currency_id', ''))
        brand.is_active = is_active
        brand.name = name
        brand.link = link
        brand.code = code
        brand.currency_id = currency_id
        brand.save()
        countries = request.data.get('countries')
        for i in countries:
            brand_country = None
            try:
                brand_country = BrandCountry.objects.get(brand_id=brand.id, country_id=int(i['country_id']))
            except:
                pass
            if brand_country is None:
                brand_country = BrandCountry()
                brand_country.brand = brand
                brand_country.country_id = int(i['country_id'])
            brand_country.mark_up = i['mark_up']
            brand_country.round_digit = i['round_digit']
            brand_country.round_to = i['round_to']
            brand_country.save()

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
        department = VendDepartment.objects.get(id=id)
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
            depart.name = request.data.get('name', '')
            depart.code = request.data.get('code', '').upper()
            depart.is_active = request.data.get('is_active', True)
            depart.save()
            for i in request.data.get('languages'):
                tr = None
                try:
                    tr = TranslationDepartment.objects.create(department=depart, language_id=int(i['lang_id']),
                                                              name=i['translation'], is_active=i['is_active'])
                    tr.save()
                except:
                    pass
        else:
            depart = Department.objects.get(id=department_id)
        department.department = depart
        department.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def operator_categories_item_view(request, id):
    category = None
    try:
        category = VendCategory.objects.get(id=id)
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
            izi_category = Category()
            izi_category.code = request.data.get('code', '').upper()
            izi_category.position = request.data.get('position', 1)
            izi_category.parent_id = int(request.data.get('parent_id'))
            izi_category.name = request.data.get('name', '')
            izi_category.is_active = request.data.get('is_active', True)
            izi_category.save()
            for i in request.data.get('languages'):
                tr = None
                try:
                    tr = TranslationCategory.objects.create(category=izi_category, language_id=int(i['lang_id']),
                                                            name=i['translation'], is_active=i['is_active'])
                    tr.save()
                except:
                    pass
        else:
            izi_category = Category.objects.get(id=category_id)
        category.category = izi_category
        category.save()
        # with transaction.atomic():
        #     categories = VendCategory.objects.filter(name=category.name, category__isnull=True)
        #     for i in categories:
        #         i.category = category.category
        #         i.save()
        # products = Product.objects.filter(category__isnull=True, link__tr_category=category)
        # for j in products:
        #     j.category = category.category
        #     j.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        category.category = None
        category.save()
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
        category.position = request.data.get('position', 1)
        category.code = request.data.get('code', '').upper()
        category.is_active = request.data.get('is_active', True)
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationDepartment.objects.create(department=category, language_id=int(i['lang_id']),
                                                          name=i['translation'], is_active=i['is_active'])
                tr.save()
            except:
                pass
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_colours_view(request):
    if request.method == 'GET':
        colours = VendColour.objects.all()
        return Response(status=status.HTTP_200_OK, data=VendColourSerializer(colours, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_izishop_colours_view(request):
    if request.method == 'GET':
        colours = IziColour.objects.all()
        return Response(status=status.HTTP_200_OK, data=IziColorSerializer(colours, many=True).data)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        is_active = request.data.get('is_active', True)
        code = request.data.get('code', '').upper()
        colour = IziColour()
        colour.name = name
        colour.code = code
        colour.is_active = is_active
        colour.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationColour.objects.create(colour=colour, language_id=int(i['lang_id']),
                                                      name=i['translation'])
                tr.save()
            except:
                pass
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def operator_izishop_colours_item_view(request, id):
    colour = IziColour.objects.get(id=id)
    if request.method == 'PUT':
        colour.code = request.data.get('code', '').upper()
        colour.name = request.data.get('name', '')
        is_active = request.data.get('is_active', True)
        colour.is_active = is_active
        colour.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationColour.objects.get(colour=colour, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationColour.objects.create(colour=colour, language_id=int(i['lang_id']),
                                                      name=i['translation'])
            else:
                tr.name = i['translation']
            tr.save()
    elif request.method == 'DELETE':
        colour.delete()
    return Response(status=status.HTTP_200_OK, data=IziColorSerializer(colour).data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def operator_izi_shop_sizes_item_view(request, id):
    colour = Size.objects.get(id=id)
    if request.method == 'PUT':
        colour.code = request.data.get('code', '').upper()
        colour.name = request.data.get('name', '')
        is_active = request.data.get('is_active', True)
        colour.is_active = is_active
        colour.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationSize.objects.get(size=colour, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationSize.objects.create(size=colour, language_id=int(i['lang_id']),
                                                    name=i['translation'])
            else:
                tr.name = i['translation']
            tr.save()
    elif request.method == 'DELETE':
        colour.delete()
    return Response(status=status.HTTP_200_OK, data=SizeSerializer(colour).data)


@api_view(['GET', 'PUT', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def operator_colours_item_view(request, id):
    colour = VendColour.objects.get(id=id)
    if request.method == 'PUT':
        # category.code = request.data.get('code', '')
        colour.name = request.data.get('name', '')
        colour.name_en = request.data.get('name_en', '')
        colour.save()
    elif request.method == 'POST':
        colour_id = int(request.data.get('colour_id', 1))
        if colour_id > 0:
            colour.izi_colour_id = colour_id
        else:
            colour.izi_colour = None
        colour.save()
    return Response(status=status.HTTP_200_OK, data=VendColourSerializer(colour).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_vend_size_item_view(request, id):
    size = VendSize.objects.get(id=id)
    if request.method == 'PUT':
        size.name = request.data.get('name', '')
        size.save()
    elif request.method == 'POST':
        size_id = int(request.data.get('size_id', 1))
        if size_id > 0:
            size.izi_size_id = size_id
        else:
            size.izi_size = None
        size.save()
    return Response(status=status.HTTP_200_OK, data=VendSizeSerializer(size).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_category_search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        categories = Category.objects.filter(name_lower__contains=query.lower(), parent__isnull=False)
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(categories, many=True).data)
    elif request.method == 'POST':
        name = request.data.get('name', '')
        category = Category()
        category.name = name
        category.position = request.data.get('position', 1)
        code = request.data.get('code', '').upper()
        count = Category.objects.filter(code=code).count()
        if count > 0:
            return Response(status=status.HTTP_409_CONFLICT)
        category.code = code
        category.is_active = request.data.get('is_active', True)
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationCategory.objects.create(category=category, language_id=int(i['lang_id']),
                                                        name=i['translation'], is_active=(i['is_active']))
                tr.save()
            except:
                pass
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def operator_sizes_view(request):
    if request.method == 'GET':
        sizes = VendSize.objects.all()
        return Response(status=status.HTTP_200_OK, data=VendSizeSerializer(sizes, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_izi_shop_sizes_view(request):
    if request.method == 'GET':
        sizes = Size.objects.all()
        return Response(status=status.HTTP_200_OK, data=SizeSerializer(sizes, many=True).data)
    elif request.method == 'POST':
        category = Size()
        category.code = request.data.get('code', '').upper()
        category.name = request.data.get('name', '')
        # category.position = request.data.get('position', 1)
        category.is_active = request.data.get('is_active', True)
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationSize.objects.get(size=category, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationSize.objects.create(size=category, language_id=int(i['lang_id']),
                                                    name=i['translation'], is_active=(i['is_active']))
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_izi_shop_content_view(request):
    if request.method == 'GET':
        contents = Content.objects.all()
        return Response(status=status.HTTP_200_OK, data=ContentSerializer(contents, many=True).data)
    elif request.method == 'POST':
        content = Content()
        content.code = request.data.get('code', '').upper()
        content.name = request.data.get('name', '')
        # category.position = request.data.get('position', 1)
        content.is_active = request.data.get('is_active', True)
        content.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationContent.objects.get(content=content, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationContent.objects.create(content=content, language_id=int(i['lang_id']),
                                                       name=i['translation'], is_active=(i['is_active']))
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def operator_izi_shop_content_item_view(request, id):
    content = Content.objects.get(id=id)
    if request.method == 'PUT':
        content.code = request.data.get('code', '').upper()
        content.name = request.data.get('name', '')
        is_active = request.data.get('is_active', True)
        content.is_active = is_active
        content.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationContent.objects.get(content=content, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationContent.objects.create(content=content, language_id=int(i['lang_id']),
                                                       name=i['translation'])
            else:
                tr.name = i['translation']
            tr.save()
    elif request.method == 'DELETE':
        content.delete()
    return Response(status=status.HTTP_200_OK, data=ContentSerializer(content).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_parent_category_search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        categories = ParentCategory.objects.filter(name_lower__contains=query.lower())
        return Response(status=status.HTTP_200_OK, data=ParentCategorySerializer(categories, many=True).data)
    elif request.method == 'POST':
        category = ParentCategory()
        category.code = request.data.get('code', '').upper()
        category.name = request.data.get('name', '')
        category.position = request.data.get('position', 1)
        category.is_active = request.data.get('is_active', True)
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationParentCategory.objects.get(category=category, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationParentCategory.objects.create(category=category, language_id=int(i['lang_id']),
                                                              name=i['translation'], is_active=(i['is_active']))
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def operator_category_item_view(request, id):
    category = Category.objects.get(id=id)
    if request.method == 'PUT':
        code = request.data.get('code', '').upper()
        count = Category.objects.exclude(id__in=[category.id]).filter(code=code).count()
        if count > 0:
            return Response(status=status.HTTP_409_CONFLICT)
        category.code = code
        category.name = request.data.get('name', '')
        category.position = request.data.get('position', 1)
        category.is_active = request.data.get('is_active', True)
        try:
            category.parent_id = int(request.data.get('parent_id', ''))
        except:
            pass
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationCategory.objects.get(category=category, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationCategory.objects.create(category=category, language_id=int(i['lang_id']),
                                                        name=i['translation'], is_active=(i['is_active']))
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(category).data)
    elif request.method == 'GET':
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(category).data)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def operator_parent_category_item_view(request, id):
    category = ParentCategory.objects.get(id=id)
    if request.method == 'PUT':
        category.code = request.data.get('code', '').upper()
        category.name = request.data.get('name', '')
        category.position = request.data.get('position', 1)
        category.is_active = request.data.get('is_active', True)
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationParentCategory.objects.get(category=category, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationParentCategory.objects.create(category=category, language_id=int(i['lang_id']),
                                                              name=i['translation'], is_active=(i['is_active']))
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK, data=ParentCategorySerializer(category).data)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def operator_department_item_view(request, id):
    deparment = Department.objects.get(id=id)
    if request.method == 'PUT':
        deparment.code = request.data.get('code', '').upper()
        deparment.name = request.data.get('name', '')
        deparment.position = request.data.get('position', 1)
        deparment.is_active = request.data.get('is_active', True)
        deparment.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationDepartment.objects.get(department=deparment, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationDepartment.objects.create(department=deparment, language_id=int(i['lang_id']),
                                                          name=i['translation'], is_active=i['is_active'])
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK, data=DepartmentSerializer(deparment).data)
    elif request.method == 'GET':
        return Response(data=DepartmentSerializer(deparment).data)
    elif request.method == 'DELETE':
        deparment.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def operator_department_item_parents_view(request, deparment_id):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        categories = ParentCategory.objects.filter(name_lower__contains=query.lower(), department_id=deparment_id)
        return Response(status=status.HTTP_200_OK, data=ParentCategorySerializer(categories, many=True).data)
    elif request.method == 'POST':
        category = ParentCategory()
        category.code = request.data.get('code', '').upper()
        category.name = request.data.get('name', '')
        category.department_id = deparment_id
        category.position = request.data.get('position', 1)
        category.is_active = request.data.get('is_active', True)
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationParentCategory.objects.get(parent_category=category, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationParentCategory.objects.create(parent_category=category, language_id=int(i['lang_id']),
                                                              name=i['translation'], is_active=(i['is_active']))
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def operator_department_parents_categories_view(request, parent_id):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        categories = Category.objects.filter(name_lower__contains=query.lower(), parent_id=parent_id)
        return Response(status=status.HTTP_200_OK, data=CategorySerializer(categories, many=True).data)
    elif request.method == 'POST':
        category = Category()
        code = request.data.get('code', '').upper()
        count = Category.objects.filter(code=code).count()
        if count > 0:
            return Response(status=status.HTTP_409_CONFLICT)
        category.code = code
        category.name = request.data.get('name', '')
        category.parent_id = parent_id
        category.position = request.data.get('position', 1)
        category.is_active = request.data.get('is_active', True)
        category.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationCategory.objects.get(category=category, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationCategory.objects.create(category=category, language_id=int(i['lang_id']),
                                                        name=i['translation'], is_active=(i['is_active']))
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def operator_department_parents_item_view(request, id):
    parent = ParentCategory.objects.get(id=id)
    if request.method == 'PUT':
        parent.code = request.data.get('code', '').upper()
        parent.name = request.data.get('name', '')
        try:
            parent.department_id = int(request.data.get('department_id', ''))
        except:
            pass
        parent.position = request.data.get('position', 1)
        parent.is_active = request.data.get('is_active', True)
        parent.save()
        for i in request.data.get('languages'):
            tr = None
            try:
                tr = TranslationParentCategory.objects.get(parent_category=parent, language_id=int(i['lang_id']))
            except:
                pass
            if tr is None:
                tr = TranslationParentCategory.objects.create(parent_category=parent, language_id=int(i['lang_id']),
                                                              name=i['translation'], is_active=i['is_active'])
            else:
                tr.name = i['translation']
            tr.save()
        return Response(status=status.HTTP_200_OK, data=ParentCategorySerializer(parent).data)
    elif request.method == 'GET':
        return Response(data=ParentCategorySerializer(parent).data)
    elif request.method == 'DELETE':
        parent.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def categories_zara_list_view(request):
    if request.method == 'GET':
        categories = VendCategory.objects.filter(is_active=True, department__brand__is_active=True,
                                                 department__is_active=True,
                                                 department__brand__link='https://www.zara.com/tr/')
        return Response(data=TrendYolCategoryDetailedSerializer(categories, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        with transaction.atomic():
            for i in request.data:
                category = VendCategory.objects.get(id=int(i['category_id']))
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
def categories_handm_list_view(request):
    if request.method == 'GET':
        categories = VendCategory.objects.filter(is_active=True, department__brand__is_active=True,
                                                 department__is_active=True,
                                                 department__brand__link='https://www2.hm.com/tr_tr/')
        return Response(data=TrendYolCategoryDetailedSerializer(categories, many=True).data, status=status.HTTP_200_OK)
    else:
        for i in request.data:
            category = VendCategory.objects.get(id=int(i['id']))
            for j in i['categories']:
                c = None
                try:
                    c = VendCategory.objects.get(name=j['category'])
                except:
                    pass
                if c is None:
                    c = VendCategory.objects.create(name=j['category'], link=j['link'], department=category.department)
                    c.save()
            if len(i['categories']) > 0:
                category.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def handm_item_view(request):
    zara = None
    if request.method == 'GET':
        try:
            zara = Brand.objects.get(link='https://www2.hm.com/tr_tr/')
        except:
            pass
        return Response(data=BrandSerializer(zara).data, status=status.HTTP_200_OK)
    else:
        try:
            zara = Brand.objects.get(link='https://www2.hm.com/tr_tr/')
        except:
            pass
        if zara is not None:
            for i in request.data:
                department_name = i['department']
                department = None
                try:
                    department = VendDepartment.objects.get(brand=zara, name=department_name)
                except:
                    pass
                if department is None:
                    department = VendDepartment.objects.create(brand=zara, name=department_name)
                    department.save()
                    for j in i['categories']:
                        category_name = j['name']
                        category_link = j['link']
                        category = None
                        try:
                            category = VendCategory.objects.get(department=department, name=category_name,
                                                                link=category_link)
                        except:
                            pass
                        if category is None:
                            category = VendCategory.objects.create(department=department, name=category_name,
                                                                   link=category_link)
                            category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def zara_item_view(request):
    zara = None
    if request.method == 'GET':
        try:
            zara = Brand.objects.get(link='https://www.zara.com/tr/')
        except:
            pass
        return Response(data=BrandSerializer(zara).data, status=status.HTTP_200_OK)
    else:
        try:
            zara = Brand.objects.get(link='https://www.zara.com/tr/')
        except:
            pass
        if zara is not None:
            for i in request.data:
                department_name = i['department']
                department = None
                try:
                    department = VendDepartment.objects.get(brand=zara, name=department_name)
                except:
                    pass
                if department is None:
                    department = VendDepartment.objects.create(brand=zara, name=department_name)
                    department.save()
                    for j in i['categories']:
                        category_name = j['category']
                        category_link = j['link']
                        category = None
                        try:
                            category = VendCategory.objects.get(department=department, name=category_name,
                                                                link=category_link)
                        except:
                            pass
                        if category is None:
                            category = VendCategory.objects.create(department=department, name=category_name,
                                                                   link=category_link)
                            category.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsOperator])
def operator_documents_view(request):
    if request.method == 'GET':
        documents = Document.objects.filter(user=request.user)
        return Response(status=status.HTTP_200_OK, data=DocumentSerializer(documents, many=True).data)


@api_view(['GET'])
@permission_classes([IsOperator])
def operator_documents_all_view(request):
    if request.method == 'GET':
        documents = Document.objects.all()
        return Response(status=status.HTTP_200_OK, data=DocumentSerializer(documents, many=True).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_documents_item_view(request, id):
    try:
        document = Document.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':

        return Response(status=status.HTTP_200_OK, data=DocumentDetailedSerializer(document).data)
    elif request.method == 'PUT':
        document = Document.objects.get(id=id)
        document.user = request.user
        document.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_documents_process_view(request, id):
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
        data['colours'] = IziColourSerializer(IziColour.objects.all(), many=True).data
        data['contents'] = ContentSerializer(Content.objects.all(), many=True).data
        data['comments'] = CommentSerializer(DocumentComment.objects.filter(document=document), many=True).data
        return Response(status=status.HTTP_200_OK, data=data)
    elif request.method == 'POST':
        document.step = document.step + 1
        document.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_documents_process_products_view(request, id):
    try:
        document = Document.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        query = request.GET.get('query', '')
        page = int(request.GET.get('page', 1))

        data = {}
        products = OriginalProduct.objects.filter(document_product__document=document, stock=True, original_price__gt=0)
        if query != "":
            if query[0] == '-':
                products = products.exclude(title_lower__contains=query[1:])
            else:
                products = products.filter(Q(title_lower__contains=query) | Q(description__contains=query))
        department_id = None
        try:
            department_id = int(request.GET.get('department_id', ''))
        except:
            pass
        if department_id is not None and department_id != 0:
            products = products.filter(link__product__department_id=department_id)
        elif department_id is not None and department_id == 0:
            products = products.filter(link__product__department__isnull=True)
        category_id = None
        try:
            category_id = int(request.GET.get('category_id', ''))
        except:
            pass
        if category_id is not None and category_id != 0:
            products = products.filter(link__product__category_id=category_id)
        elif category_id is not None and category_id == 0:
            products = products.filter(link__product__category__isnull=True)
        colour_id = None
        try:
            colour_id = int(request.GET.get('colour_id', ''))
        except:
            pass
        if colour_id is not None and colour_id != 0:
            products = products.filter(link__product__colour_id=colour_id)
        elif colour_id is not None and colour_id == 0:
            products = products.filter(link__product__colour__isnull=True)

        content_id = None
        try:
            content_id = int(request.GET.get('content_id', ''))
        except:
            pass
        if content_id is not None and content_id != 0:
            products = products.filter(link__product__content_id=content_id)
        elif content_id is not None and content_id == 0:
            products = products.filter(link__product__content__isnull=True)
        length = products.count()
        pages = length // 200
        if pages == 0:
            pages = 1
        elif length % 200 != 0:
            pages += 1
        data['count'] = length
        data['pages'] = pages
        data['products'] = ProductSerializer(products[(page - 1) * 200:page * 200], many=True).data
        return Response(status=status.HTTP_200_OK, data=data)
    # elif request.method == 'POST':
    #     with transaction.atomic():
    #         for i in request.data.get('products'):
    #             try:
    #                 product = OriginalProduct.objects.get(id=int(i))
    #             except:
    #                 pass
    #             if product is not None:
    #                 document_product = DocumentProduct.objects.get(document=document, product=product)
    #                 document_product.step = document.step + 1
    #                 document_product.save()
    #         size = DocumentProduct.objects.filter(document=document, step=document.step).count()
    #         if size == 0:
    #             document.step = document.step + 1
    #             document.save()
    #         return Response(status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        with transaction.atomic():
            option = request.data.get('option', '')
            id = None
            try:
                id = int(request.data.get('id', ''))
            except:
                pass
            for i in request.data.get('products'):
                try:
                    product = OriginalProduct.objects.get(id=int(i))
                    izi = product.link.product
                    if option == 'department':
                        izi.department_id = id
                        izi.category = None
                    elif option == 'category':
                        izi.category_id = id
                    elif option == 'colour':
                        izi.colour_id = id
                    elif option == 'content':
                        izi.content_id = id
                    izi.save()
                    product.save()
                except:
                    pass
        return Response(status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsOperator])
def operator_documents_process_products_item_view(request, id, product_id):
    try:
        document = Document.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        with transaction.atomic():
            option = request.data.get('option', '')
            id = None
            try:
                id = int(request.data.get('id', ''))
            except:
                pass
            product = OriginalProduct.objects.get(id=product_id, document_product__document=document)
            izi = product.link.product
            if option == 'department':
                izi.department_id = id
                izi.category = None
            elif option == 'category':
                izi.category_id = id
            elif option == 'colour':
                izi.colour_id = id
            elif option == 'content':
                izi.content_id = id
            izi.save()
            product.save()
            return Response(status=status.HTTP_200_OK, data=ProductSerializer(product).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def operator_documents_products_view(request, id):
    try:
        document = Document.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        products = OriginalProduct.objects.filter(document_product__document=document)
        query = request.GET.get('query', '')
        products = products.filter(title__contains=query)
        category_id = None
        try:
            category_id = int(request.GET.get('category_id'))
        except:
            pass
        if category_id is not None:
            products = products.filter(category_id=category_id)
        colour_id = None
        try:
            colour_id = int(request.GET.get('colour_id'))
        except:
            pass
        if colour_id is not None:
            products = products.filter(colour_id=colour_id)
        return Response(status=status.HTTP_200_OK, data=ProductSerializer(products, many=True).data)
    else:
        data = request.data.get('products', [])
        name = request.data.get('attribute_name', '')
        id = int(request.data.get('attribute_id', ''))
        for i in data:
            product = Product.objects.get(link__originalproduct=OriginalProduct.objects.get(id=i))
            if name == 'colour':
                product.colour_id = id
            elif name == 'category':
                product.category_id = id
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def operator_documents_products_brands_view(request, id):
    try:
        document = Document.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        department = document.department
        return Response(status=status.HTTP_200_OK, data=TrendYolDepartmentDetailedSerializer(department).data)


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


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def operator_vendor_products_item_view(request, id):
    if request.method == 'PUT':
        product = OriginalProduct.objects.get(id=id)
        product.is_active = request.data.get('is_active', True)
        product.save()
        return Response(status=status.HTTP_200_OK, data=ProductSerializer(product).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def operator_vendor_products_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        page = int(request.GET.get('page', 1))

        data = {}
        products = OriginalProduct.objects.all()
        if query != "":
            if query[0] == '-':
                products = products.exclude(title_lower__contains=query[1:])
            else:
                products = products.filter(Q(title_lower__contains=query) | Q(description__contains=query) |
                                           Q(product_code__contains=query) | Q(product_id__contains=query))
        brand_id = None
        try:
            brand_id = int(request.GET.get('brand_id', ''))
        except:
            pass
        if brand_id is not None and brand_id != 0:
            products = products.filter(brand_id=brand_id)
        elif brand_id is not None and brand_id == 0:
            products = products.filter(brand__isnull=True)
        department_id = None
        try:
            department_id = int(request.GET.get('department_id', ''))
        except:
            pass
        if department_id is not None and department_id != 0:
            products = products.filter(department_id=department_id)
        elif department_id is not None and department_id == 0:
            products = products.filter(department__isnull=True)
        category_id = None
        try:
            category_id = int(request.GET.get('category_id', ''))
        except:
            pass
        if category_id is not None and category_id != 0:
            products = products.filter(category_id=category_id)
        elif category_id is not None and category_id == 0:
            products = products.filter(category__isnull=True)
        colour_id = None
        try:
            colour_id = int(request.GET.get('colour_id', ''))
        except:
            pass
        if colour_id is not None and colour_id != 0:
            products = products.filter(colour_id=colour_id)
        elif colour_id is not None and colour_id == 0:
            products = products.filter(colour__isnull=True)
        length = products.count()
        pages = length // 200
        if pages == 0:
            pages = 1
        elif length % 200 != 0:
            pages += 1
        data['count'] = length
        data['pages'] = pages
        data['products'] = ProductSerializer(products[(page - 1) * 200:page * 200], many=True).data
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def operator_izi_shop_products_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        page = int(request.GET.get('page', 1))

        data = {}
        products = Product.objects.filter(link__originalproduct__document_product__document__step=100,
                                          link__originalproduct__selling_price__gt=0)
        if query != "":
            if query[0] == '-':
                products = products.exclude(link__originalproduct__title_lower__contains=query[1:])
            else:
                products = products.filter(Q(link__originalproduct__title_lower__contains=query) | Q(
                    link__originalproduct__description__contains=query) |
                                           Q(link__originalproduct__product_code__contains=query) | Q(
                    link__originalproduct__product_id__contains=query))
        department_id = None
        try:
            department_id = int(request.GET.get('department_id', ''))
        except:
            pass
        if department_id is not None and department_id != 0:
            products = products.filter(department_id=department_id)
        elif department_id is not None and department_id == 0:
            products = products.filter(department__isnull=True)
        category_id = None
        try:
            category_id = int(request.GET.get('category_id', ''))
        except:
            pass
        if category_id is not None and category_id != 0:
            products = products.filter(category_id=category_id)
        elif category_id is not None and category_id == 0:
            products = products.filter(category__isnull=True)
        colour_id = None
        try:
            colour_id = int(request.GET.get('colour_id', ''))
        except:
            pass
        if colour_id is not None and colour_id != 0:
            products = products.filter(colour_id=colour_id)
        elif colour_id is not None and colour_id == 0:
            products = products.filter(colour__isnull=True)

        content_id = None
        try:
            content_id = int(request.GET.get('content_id', ''))
        except:
            pass
        if content_id is not None and content_id != 0:
            products = products.filter(content_id=content_id)
        elif content_id is not None and content_id == 0:
            products = products.filter(content__isnull=True)
        length = products.count()
        pages = length // 200
        if pages == 0:
            pages = 1
        elif length % 200 != 0:
            pages += 1
        data['count'] = length
        data['pages'] = pages
        data['products'] = IziShopProductSerializer(products[(page - 1) * 200:page * 200], many=True).data
        return Response(status=status.HTTP_200_OK, data=data)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def operator_izi_shop_products_item_view(request, product_id):
    if request.method == 'PUT':
        with transaction.atomic():
            option = request.data.get('option', '')
            id = None
            try:
                id = int(request.data.get('id', ''))
            except:
                pass
            izi = Product.objects.get(id=product_id)
            if id is not None:
                if option == 'department':
                    izi.department_id = id
                elif option == 'category':
                    izi.category_id = id
                elif option == 'colour':
                    izi.colour_id = id
                elif option == 'content':
                    izi.content_id = id

            izi.save()
            return Response(status=status.HTTP_200_OK, data=IziShopProductSerializer(izi).data)
    elif request.method == 'POST':
        izi = Product.objects.get(id=product_id)
        izi.is_sellable = request.data.get('is_sellable', True)
        izi.save()
        return Response(status=status.HTTP_200_OK, data=IziShopProductSerializer(izi).data)
