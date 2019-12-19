from django.db.models import Q
from rest_framework import serializers

from product_app.models import Brand, VendDepartment, VendCategory, Link, Document, OriginalProduct, Currency, Language, \
    ExchangeRate, ExchangeValue, Country, DocumentProduct, BrandCountry
from user_app.serializers import UserSerializer


class TrendYolCategoryDetailedSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'link', 'is_active', 'data')

    def get_data(self, obj):
        links = Link.objects.filter(tr_category=obj)
        data = {
            'not_parsed': links.filter(status=4).count(),
            'out_process': links.filter(status=1).count(),
            'in_process': links.filter(status=3).count(),
            'processed': links.filter(status=2).count(),
        }
        return data


class TrendYolDepartmentDetailedSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = VendDepartment
        fields = ('id', 'name', 'is_active', 'categories')

    def get_categories(self, obj):
        categories = VendCategory.objects.filter(department=obj)
        return TrendYolCategoryDetailedSerializer(categories, many=True).data


class BrandAdminDetailedSerializer(serializers.ModelSerializer):
    total_count = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()
    processed_count = serializers.SerializerMethodField()
    in_process_count = serializers.SerializerMethodField()
    out_process_count = serializers.SerializerMethodField()
    no_price_or_stock = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'is_active', 'total_count', 'document_count', 'processed_count', 'in_process_count',
                  'out_process_count', 'no_price_or_stock')

    def get_total_count(self, obj):
        count = OriginalProduct.objects.filter(brand=obj).count()
        return count

    def get_no_price_or_stock(self, obj):
        count = OriginalProduct.objects.filter(Q(original_price=0) | Q(stock=False), brand=obj).count()
        return count

    def get_document_count(self, obj):
        count = Document.objects.filter(brand=obj).count()
        return count

    def get_processed_count(self, obj):
        count = DocumentProduct.objects.filter(document__brand=obj, step=4).count()
        return count

    def get_in_process_count(self, obj):
        count = DocumentProduct.objects.filter(document__brand=obj, step__in=[1, 2, 3]).count()
        return count

    def get_out_process_count(self, obj):
        count = (OriginalProduct.objects.filter(document_product__document__isnull=True, brand=obj).count())
        return count


class CurrencySerializer(serializers.ModelSerializer):
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = 'id code name code_name is_active is_related'.split()

    def get_is_related(self, obj):
        count = Country.objects.filter(currency=obj).count()
        if count > 0:
            return True
        count = Brand.objects.filter(currency=obj).count()
        if count > 0:
            return True
        return False


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeValue
        fields = '__all__'


class ExchangeRateSerializer(serializers.ModelSerializer):
    from_currency = CurrencySerializer()
    to_currency = CurrencySerializer()
    values = ValueSerializer(many=True)
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = ExchangeRate
        fields = 'id from_currency to_currency date value values is_related'.split()

    def get_is_related(self, obj):
        return True


class LanguageSerializer(serializers.ModelSerializer):
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = Language
        fields = 'id code name is_translate is_active is_related'.split()

    def get_is_related(self, obj):
        count = Country.objects.filter(language=obj).count()
        if count > 0:
            return True
        return False


class CountrySerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()
    language = LanguageSerializer()
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = 'id code name currency language is_active is_related'.split()

    def get_is_related(self, obj):
        if obj.currency is None and obj.language is None:
            return False
        return True


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendDepartment
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    no_stock_or_price = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ('id', 'updated_at', 'user', 'step', 'status', 'department', 'brand', 'products', 'no_stock_or_price')

    def get_department(self, obj):
        try:
            return obj.department.name
        except:
            return 'Нет отделения'

    def get_no_stock_or_price(self, obj):
        count = OriginalProduct.objects.filter(Q(original_price=0) | Q(stock=False),
                                               document_product__document=obj).count()
        return count

    def get_brand(self, obj):
        try:
            return obj.department.brand.name
        except:
            return 'Нет бренда'

    def get_products(self, obj):
        return DocumentProduct.objects.filter(document=obj).count()

    def get_status(self, obj):
        return obj.status


class DocumentsSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department = DepartmentSerializer()
    brand = BrandAdminDetailedSerializer()
    products = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    no_stock_or_price = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ('id', 'updated_at', 'user', 'step', 'status', 'department', 'brand', 'products', 'no_stock_or_price')

    def get_no_stock_or_price(self, obj):
        count = OriginalProduct.objects.filter(Q(original_price=0) | Q(stock=False),
                                               document_product__document=obj).count()
        return count

    def get_products(self, obj):
        return DocumentProduct.objects.filter(document=obj).count()

    def get_status(self, obj):
        return obj.status


class DocumentDetailedSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    # brands = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ('id', 'updated_at', 'status')

    # def get_brands(self, obj):
    #     products = (obj.original_products.all())
    #     categories = VendCategory.objects.filter(id__in=[i.link.tr_category.id for i in products])
    #     departments = VendDepartment.objects.filter(id__in=[i.department_id for i in categories])
    #     brands = Brand.objects.filter(id__in=[i.brand.id for i in departments])
    #     brand_arr = []
    #     for brand in brands:
    #         department_arr = []
    #         for department in departments.filter(brand=brand):
    #             categories_arr = []
    #             for category in categories.filter(department=department):
    #                 category_data = {
    #                     'category_id': category.id,
    #                     'name': category.name
    #                 }
    #                 categories_arr.append(category_data)
    #             department_data = {
    #                 'department_id': department.id,
    #                 'name': department.name,
    #                 'categories': categories_arr
    #             }
    #             department_arr.append(department_data)
    #         brand_data = {
    #             'brand_id': brand.id,
    #             'name': brand.name,
    #             'departments': department_arr
    #         }
    #         brand_arr.append(brand_data)
    #     return brand_arr
