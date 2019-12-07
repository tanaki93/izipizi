from rest_framework import serializers

from product_app.models import Category, Department, Link, OriginalProduct, Product, ParentCategory, Country, \
    BrandCountry, Language, TranslationCategory, TranslationDepartment, VendSize, Size, TranslationColour, VendColour, \
    DocumentComment

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


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ('id', 'name')


class VendSizeSerializer(serializers.ModelSerializer):
    name_en = serializers.SerializerMethodField()

    class Meta:
        model = VendSize
        fields = ('id', 'name', 'name_en')

    def get_name_en(self, obj):
        try:
            return obj.size.name
        except:
            return obj.name


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentComment
        fields = ('id', 'text', 'updated_at')


class VendColourSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()

    class Meta:
        model = VendColour
        fields = ('id', 'name', 'languages', 'name_en')

    # def get_name(self, obj):
    #     try:
    #         language = Language.objects.get(code='ru')
    #         translation = TranslationColour.objects.get(vend_colour=obj, language=language)
    #         return translation.name.capitalize()
    #     except:
    #         pass
    #     return obj.name

    def get_languages(self, obj):
        data = []
        for i in Language.objects.all():
            tr = None
            try:
                tr = TranslationColour.objects.get(vend_colour=obj, language=i)
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

    class Meta:
        model = VendColour
        fields = ('id', 'name', 'name_ru', 'name_en')

    def get_name_ru(self, obj):
        try:
            language = Language.objects.get(code='ru')
            translation = TranslationColour.objects.get(vend_colour=obj, language=language)
            return translation.name.capitalize()
        except:
            pass
        return ''


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

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'languages', 'categories', 'code', 'position', 'is_active')

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
    currency = CurrencySerializer()

    class Meta:
        model = Brand
        fields = (
            'id', 'name', 'is_active', 'link', 'code', 'created_at', 'updated_at', 'project', 'countries', 'currency')

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

    class Meta:
        model = Department
        fields = ('id', 'name', 'languages', 'departments', 'position', 'code', 'is_active')

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
        fields = '__all__'


class VendCategoryDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'link', 'is_active',)


class VendDepartmentDetailedSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = VendDepartment
        fields = ('id', 'name', 'is_active', 'categories')

    def get_categories(self, obj):
        categories = VendCategory.objects.filter(department=obj)
        return VendCategoryDetailedSerializer(categories, many=True).data


class BrandProcessSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'is_active', 'departments')

    def get_departments(self, obj):
        departments = VendDepartment.objects.filter(brand=obj)
        return VendDepartmentDetailedSerializer(departments, many=True).data


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
    category = TrendYolCategorySerializer()
    izi_category = serializers.SerializerMethodField()
    colour = ColourSerializer()

    class Meta:
        model = OriginalProduct
        fields = ['selling_price', 'discount_price', 'is_free_argo', 'images', 'delivery_date', 'product_code', 'id',
                  'colour', 'promotions', 'created_at', 'active', 'brand', 'product_id', 'link', 'is_rush_delivery',
                  'title',
                  'original_price', 'updated_at', 'description', 'product', 'department', 'category','izi_category','izi_department', 'colour']

    def get_images(self, obj):
        return obj.images.split()

    def get_product(self, obj):
        product = Product.objects.get(link=obj.link)
        return IziProductSerializer(product).data

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