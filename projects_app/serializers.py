from rest_framework import serializers

from product_app.models import Category, Department, Link, OriginalProduct, Product, ParentCategory, Country, \
    BrandCountry, Language, TranslationCategory, TranslationDepartment, VendSize, Size, TranslationColour, VendColour, \
    DocumentComment, IziColour, TranslationSize, TranslationContent, Content, ExchangeRate

# class RecursiveSerializer(serializers.Serializer):
#     def to_representation(self, value):
#         serializer = self.parent.parent.__class__(value, context=self.context)
#         return serializer.data
from product_app.models import Brand, VendCategory, VendDepartment
from projects_app.admin_serializers import CurrencySerializer


class TrendYolDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendDepartment
        fields = ('id', 'name')


class IziSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ('id', 'name', 'code')


class SizeSerializer(serializers.ModelSerializer):
    languages = serializers.SerializerMethodField()
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = Size
        fields = ('id', 'name', 'languages', 'code', 'is_related')

    def get_is_related(self, obj):
        count = VendSize.objects.filter(izi_size=obj).count()
        if count > 0:
            return True
        return False

    def get_languages(self, obj):
        data = []
        for i in Language.objects.all():
            tr = None
            try:
                tr = TranslationSize.objects.get(size=obj, language=i)
            except:
                pass
            context = {
                'lang_id': i.id,
                'lang_name': i.name,
                'lang_code': i.code,
            }
            if tr is not None:
                context['translation'] = tr.name
            else:
                context['translation'] = None
            data.append(context)
        return data


class ContentSerializer(serializers.ModelSerializer):
    languages = serializers.SerializerMethodField()
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ('id', 'name', 'languages', 'code', 'is_related')

    def get_is_related(self, obj):
        return False

    def get_languages(self, obj):
        data = []
        for i in Language.objects.all():
            tr = None
            try:
                tr = TranslationContent.objects.get(content=obj, language=i)
            except:
                pass
            context = {
                'lang_id': i.id,
                'lang_name': i.name,
                'lang_code': i.code,
            }
            if tr is not None:
                context['translation'] = tr.name
            else:
                context['translation'] = None
            data.append(context)
        return data


class VendSizeSerializer(serializers.ModelSerializer):
    izi_size = SizeSerializer()

    class Meta:
        model = VendSize
        fields = ('id', 'name', 'izi_size')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentComment
        fields = ('id', 'text', 'updated_at')


class IziColourSerializer(serializers.ModelSerializer):
    class Meta:
        model = IziColour
        fields = '__all__'


class VendColourSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    izi_colour = IziColourSerializer()

    class Meta:
        model = VendColour
        fields = ('id', 'name', 'languages', 'name_en', 'izi_colour')

    def get_languages(self, obj):
        data = []
        for i in Language.objects.all():
            tr = None
            try:
                tr = TranslationColour.objects.get(vend_colour=obj.izi_colour, language=i)
            except:
                pass
            context = {
                'lang_id': i.id,
                'lang_name': i.name,
                'lang_code': i.code,
            }
            if tr is not None:
                context['translation'] = tr.name
            else:
                context['translation'] = None
            data.append(context)
        return data


class IziColorSerializer(serializers.ModelSerializer):
    languages = serializers.SerializerMethodField()
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = IziColour
        fields = ('id', 'name', 'languages', 'code', 'is_active', 'is_related')

    def get_is_related(self, obj):
        count = VendColour.objects.filter(izi_colour=obj).count()
        if count > 0:
            return True
        return False

    def get_languages(self, obj):
        data = []
        for i in Language.objects.all():
            tr = None
            try:
                tr = TranslationColour.objects.get(colour=obj, language=i)
            except:
                pass
            context = {
                'lang_id': i.id,
                'lang_name': i.name,
                'lang_code': i.code,
            }
            if tr is not None:
                context['translation'] = tr.name
            else:
                context['translation'] = None
            data.append(context)
        return data


class MainColourSerializer(serializers.ModelSerializer):
    name_ru = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()

    class Meta:
        model = IziColour
        fields = ('id', 'name', 'name_ru', 'languages')

    def get_name_ru(self, obj):
        try:
            language = Language.objects.all().first()
            translation = TranslationColour.objects.get(colour=obj, language=language)
            return translation.name.capitalize()
        except:
            pass
        return ''

    def get_languages(self, obj):
        data = []
        for i in Language.objects.all():
            tr = None
            try:
                tr = TranslationColour.objects.get(colour=obj, language=i)
            except:
                pass
            context = {
                'lang_id': i.id,
                'lang_name': i.name,
                'lang_code': i.code,
            }
            if tr is not None:
                context['translation'] = tr.name
            else:
                context['translation'] = None
            data.append(context)
        return data


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'


class ParentDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class ParentSerializer(serializers.ModelSerializer):
    department = ParentDepartmentSerializer()

    class Meta:
        model = ParentCategory
        fields = 'name code position id is_active department'.split()


class VendCategorySerializer(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'department', 'brand')

    def get_brand(self, obj):
        return obj.department.brand.name

    def get_department(self, obj):
        return obj.department.name


class CategorySerializer(serializers.ModelSerializer):
    parent = ParentSerializer()
    languages = serializers.SerializerMethodField()
    categories = VendCategorySerializer(many=True)
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'languages', 'categories', 'code', 'position', 'is_active', 'is_related')

    def get_is_related(self, obj):
        count = VendCategory.objects.filter(category=obj).count()
        if count > 0:
            return True
        return False

    def get_languages(self, obj):
        data = []
        languages = Language.objects.all()
        for i in languages:
            tr = None
            try:
                tr = TranslationCategory.objects.get(language=i, category=obj)
            except:
                pass
            if tr is None:
                context = {
                    'lang_id': i.id,
                    'lang_code': i.code,
                    'lang_name': i.name,
                    'translation': None,
                    'is_active': None,
                }
            else:
                context = {
                    'lang_id': i.id,
                    'lang_code': i.code,
                    'lang_name': i.name,
                    'translation': tr.name,
                    'is_active': tr.is_active,
                }
            data.append(context)
        return data


class TrendYolCategoryDetailedSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'link', 'is_active', 'category')


class TrendYolCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'is_active')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'is_active')


class BrandSerializer(serializers.ModelSerializer):
    # categories_count = serializers.SerializerMethodField()
    # departments_count = serializers.SerializerMethodField()
    project = ProjectSerializer()
    countries = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()
    currency = CurrencySerializer()

    class Meta:
        model = Brand
        fields = (
            'id', 'name', 'is_active', 'link', 'code', 'created_at', 'updated_at', 'project', 'countries', 'currency',
            'departments')

    def get_departments(self, obj):
        departments = VendDepartment.objects.filter(brand=obj)
        return TrendYolDepartmentDetailedSerializer(departments, many=True).data

    # def get_departments_count(self, obj):
    #     departments = VendDepartment.objects.filter(brand=obj).count()
    #     return departments
    #
    # def get_categories_count(self, obj):
    #     categories = VendCategory.objects.filter(department__brand=obj).count()
    #     return categories
    def get_countries(self, obj):
        countries = []
        for i in Country.objects.all():
            brand_country = None
            try:
                brand_country = BrandCountry.objects.get(country=i, brand=obj)
            except:
                pass
            if brand_country is not None:
                context = {
                    'country_id': i.id,
                    'country_name': i.name,
                    'country_code': i.code,
                    'mark_up': brand_country.mark_up,
                    'round_digit': brand_country.round_digit,
                    'round_to': brand_country.round_to,
                }
            else:
                context = {
                    'country_id': i.id,
                    'country_name': i.name,
                    'country_code': i.code,
                    'mark_up': None,
                    'round_digit': None,
                    'round_to': None,
                }
            countries.append(context)
        return countries


class VendDepartmentSerializer(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField()

    class Meta:
        model = VendDepartment
        fields = ('id', 'name', 'brand')

    def get_brand(self, obj):
        return obj.brand.name


class DepartmentSerializer(serializers.ModelSerializer):
    languages = serializers.SerializerMethodField()
    departments = VendDepartmentSerializer(many=True)
    is_related = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('id', 'name', 'languages', 'departments', 'position', 'code', 'is_active', 'is_related', 'categories')

    def get_is_related(self, obj):
        count = ParentCategory.objects.filter(department=obj).count()
        if count > 0:
            return True
        count = VendDepartment.objects.filter(department=obj).count()
        if count > 0:
            return True
        return False

    def get_categories(self, obj):
        categories = Category.objects.filter(parent__department=obj)
        return CategorySerializer(categories, many=True).data

    def get_languages(self, obj):
        data = []
        for i in Language.objects.all():
            tr = None
            try:
                tr = TranslationDepartment.objects.get(department=obj, language=i)
            except:
                pass
            context = {
                'lang_id': i.id,
                'lang_name': i.name,
                'lang_code': i.code,
            }
            if tr is not None:
                context['translation'] = tr.name
                context['is_active'] = tr.is_active
            else:
                context['translation'] = None
                context['is_active'] = None
            data.append(context)
        return data


class CategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class BrandItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class IziProductSerializer(serializers.ModelSerializer):
    # brand = BrandItemSerializer()
    # category = CategoryItemSerializer()
    # department = DepartmentSerializer()

    class Meta:
        model = Product
        fields = ['id', 'link', 'created_at', 'title',
                  'updated_at', 'description']


class TrendYolDepartmentDetailedSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = VendDepartment
        fields = ('id', 'name', 'department', 'is_active', 'categories')

    def get_categories(self, obj):
        categories = VendCategory.objects.filter(department=obj)
        return TrendYolCategoryDetailedSerializer(categories, many=True).data


class BrandDetailedSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'is_active', 'departments')

    def get_departments(self, obj):
        departments = VendDepartment.objects.filter(brand=obj)
        return TrendYolDepartmentDetailedSerializer(departments, many=True).data


class ColourSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendColour
        fields = ('id', 'name', 'name_en')


class VendCategoryDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'link', 'is_active',)


class CategoryDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active',)


class VendDepartmentDetailedSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = VendDepartment
        fields = ('id', 'name', 'is_active', 'categories')

    def get_categories(self, obj):
        categories = VendCategory.objects.filter(department=obj)
        return VendCategoryDetailedSerializer(categories, many=True).data


class DepartmentDetailedSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('id', 'name', 'is_active', 'categories')

    def get_categories(self, obj):
        categories = Category.objects.filter(parent__department=obj)
        return CategoryDetailedSerializer(categories, many=True).data


class BrandProcessSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'is_active', 'departments')

    def get_departments(self, obj):
        departments = Department.objects.filter(departments__brand=obj)
        return DepartmentDetailedSerializer(departments, many=True).data


class VendBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    link = LinkSerializer()
    images = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    department = TrendYolDepartmentSerializer()
    izi_department = serializers.SerializerMethodField()
    brand = VendBrandSerializer()
    vend_colour = serializers.SerializerMethodField()
    category = TrendYolCategorySerializer()
    izi_category = serializers.SerializerMethodField()
    colour = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = OriginalProduct
        fields = ['selling_price', 'discount_price', 'is_free_argo', 'images', 'delivery_date', 'product_code', 'id',
                  'colour', 'promotions', 'created_at', 'is_active', 'brand', 'product_id', 'link', 'is_rush_delivery',
                  'title',
                  'original_price', 'updated_at', 'description', 'product', 'department', 'category', 'izi_category',
                  'izi_department', 'colour', 'content', 'vend_colour']

    def get_images(self, obj):
        return obj.images.split()

    def get_product(self, obj):
        product = Product.objects.get(link=obj.link)
        return IziProductSerializer(product).data

    def get_vend_colour(self, obj):
        return ColourSerializer(obj.colour).data

    def get_colour(self, obj):
        return IziColourSerializer(obj.link.product.colour).data

    def get_content(self, obj):
        return ContentSerializer(obj.link.product.content).data

    def get_izi_category(self, obj):
        category = None
        try:
            product = Product.objects.get(link=obj.link)
            category = product.category
        except:
            pass
        return CategoryItemSerializer(category).data

    def get_izi_department(self, obj):
        department = None
        try:
            product = Product.objects.get(link=obj.link)
            department = product.department
        except:
            pass
        return ParentDepartmentSerializer(department).data


class VendProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    department = TrendYolDepartmentSerializer()
    brand = VendBrandSerializer()
    vend_colour = serializers.SerializerMethodField()
    category = TrendYolCategorySerializer()

    class Meta:
        model = OriginalProduct
        fields = ['selling_price', 'discount_price', 'is_free_argo', 'images', 'delivery_date', 'product_code', 'id',
                  'colour', 'promotions', 'created_at', 'is_active', 'brand', 'product_id', 'is_rush_delivery',
                  'title',
                  'original_price', 'updated_at', 'description', 'department', 'category', 'vend_colour']

    def get_images(self, obj):
        return obj.images.split()

    def get_vend_colour(self, obj):
        return ColourSerializer(obj.colour).data


class IziShopProductSerializer(serializers.ModelSerializer):
    link = LinkSerializer()
    department = ParentDepartmentSerializer()
    category = CategoryItemSerializer()
    colour = IziColourSerializer()
    content = ContentSerializer()
    vend_product = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'created_at', 'link', 'updated_at', 'department', 'category', 'colour',
                  'content', 'vend_product', 'is_sellable', 'prices']

    def get_vend_product(self, obj):
        return VendProductSerializer(obj.link.originalproduct).data

    def get_prices(self, obj):
        brand_country = BrandCountry.objects.filter(brand=obj.link.originalproduct.brand)
        data = []
        for i in brand_country:
            new_obj = {
                'country': i.country.code
            }
            price = None
            try:
                exchange = ExchangeRate.objects.get(from_currency=i.brand.currency, to_currency=i.country.currency)
                price = round((round(obj.link.originalproduct.selling_price) * exchange.value * i.mark_up) / 100,
                              i.round_digit) * 100
            except:
                pass
            if price is not None:
                new_obj['selling_price'] = price
            else:
                new_obj['selling_price'] = 0
            data.append(new_obj)
        return data
