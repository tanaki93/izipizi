from rest_framework import serializers

from product_app.models import Category, ParentCategory, Brand, Department, Slider, ImageSlider, Product, \
    OriginalProduct, Country, BrandCountry, ExchangeRate, Language, TranslationDepartment, TranslationCategory, \
    VendDepartment, VendCategory, Variant, Size, TranslationParentCategory

# class RecursiveSerializer(serializers.Serializer):
#     def to_representation(self, value):
#         serializer = self.parent.parent.__class__(value, context=self.context)
#         return serializer.data
from projects_app.serializers import VendColourSerializer, VendBrandSerializer, MainColourSerializer, SizeSerializer, \
    VendSizeSerializer, DepartmentSerializer


class CategorySerializer(serializers.ModelSerializer):
    name_ru = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = VendCategory
        fields = ('id', 'name', 'name_ru')

    def get_name_ru(self, obj):
        try:
            language = Language.objects.get(code='ru')
            translation = TranslationCategory.objects.get(category=obj.category, language=language)
            return translation.name.capitalize()
        except:
            pass
        return ''

    def get_name(self, obj):
        try:
            return obj.category.name
        except:
            pass
        return ''

    def get_id(self, obj):
        try:
            return obj.category.id
        except:
            pass
        return 0


class ChildCategorySerializer(serializers.ModelSerializer):
    name_ru = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'name_ru')

    def get_name_ru(self, obj):
        try:
            language = Language.objects.get(code='ru')
            translation = TranslationCategory.objects.get(category=obj, language=language)
            return translation.name.capitalize()
        except:
            pass
        return ''


class IziDepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = 'id name'.split()


class ParentCategorySerializer(serializers.ModelSerializer):
    childs = serializers.SerializerMethodField()
    department = IziDepSerializer()
    languages = serializers.SerializerMethodField()
    is_related = serializers.SerializerMethodField()
    class Meta:
        model = ParentCategory
        fields = ('id', 'name', 'childs', 'code', 'position', 'is_active', 'languages', 'department', 'is_related')

    def get_is_related(self, obj):
        count = Category.objects.filter(parent=obj).count()
        if count > 0:
            return True
        return False

    def get_childs(self, obj):
        return ChildCategorySerializer(Category.objects.filter(parent=obj), many=True).data

    def get_languages(self, obj):
        data = []
        languages = Language.objects.all()
        for i in languages:
            tr = None
            try:
                tr = TranslationParentCategory.objects.get(language=i, parent_category=obj)
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


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class DepartmentsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    name_ru = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = VendDepartment
        fields = ('id', 'name', 'name_ru')

    def get_name_ru(self, obj):
        try:
            language = Language.objects.get(code='ru')
            translation = TranslationDepartment.objects.get(department=obj.department, language=language)
            return translation.name.capitalize()
        except:
            pass
        return ''

    def get_name(self, obj):
        try:
            return obj.department.name
        except:
            pass
        return ''

    def get_id(self, obj):
        try:
            return obj.department.id
        except:
            pass
        return 0


class DepartmentSerializer(serializers.ModelSerializer):
    parent_categories = serializers.SerializerMethodField()
    name_ru = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('id', 'name', 'name_ru', 'parent_categories')

    def get_parent_categories(self, obj):
        categories = Category.objects.filter(categories__department__department=obj)
        parents = []
        l = ParentCategory.objects.filter(childs__in=categories)
        for i in l:
            if i not in parents:
                parents.append(i)
        return ParentCategorySerializer(parents, many=True).data

    def get_name_ru(self, obj):
        try:
            language = Language.objects.get(code='ru')
            translation = TranslationDepartment.objects.get(department=obj, language=language)
            return translation.name.capitalize()
        except:
            pass
        return ''


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSlider
        fields = '__all__'


class SliderSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Slider
        fields = ('id', 'title', 'images')


def get_price(price):
    try:
        brand_country = BrandCountry.objects.all().first()
        exchange = ExchangeRate.objects.all().first()
        x = round(price * brand_country.mark_up, brand_country.round_digit)
        return round(x * exchange.value)
    except:
        return 0


class VariantsSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = 'stock size'.split()

    def get_size(self, obj):
        try:
            size = Size.objects.get(id=obj.tr_size.id)
            return VendSizeSerializer(size).data
        except:
            return None


class MainProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()
    brand = VendBrandSerializer()
    department = DepartmentsSerializer()
    category = CategorySerializer()
    colour = MainColourSerializer()
    variants = VariantsSerializer(many=True)

    class Meta:
        model = OriginalProduct
        fields = ['discount_price', 'images', 'id', 'parent_category',
                  'colour', 'created_at', 'title',
                  'original_price', 'updated_at', 'description',
                  'brand', 'department', 'category', 'colour', 'variants']

    def get_images(self, original):
        return original.images.split()

    def get_parent_category(self, obj):
        data = None
        try:
            data = {
                'id': obj.category.category.parent_id,
                'name': obj.category.category.parent.name,
            }
        except:
            pass
        return data

    def get_original_price(self, obj):
        # print(obj.link.url)
        return get_price(obj.original_price)

    def get_discount_price(self, obj):
        # print(obj.link.url)
        return get_price(obj.discount_price)
