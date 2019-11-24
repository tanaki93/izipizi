from rest_framework import serializers

from product_app.models import Category, ParentCategory, Brand, Department, Slider, ImageSlider, Product, \
    OriginalProduct, Country, BrandCountry, ExchangeRate


# class RecursiveSerializer(serializers.Serializer):
#     def to_representation(self, value):
#         serializer = self.parent.parent.__class__(value, context=self.context)
#         return serializer.data
from projects_app.serializers import VendColourSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image')


class ParentCategorySerializer(serializers.ModelSerializer):
    childs = serializers.SerializerMethodField()

    class Meta:
        model = ParentCategory
        fields = ('id', 'name', 'childs')

    def get_childs(self, obj):
        return CategorySerializer(Category.objects.filter(parent=obj), many=True).data


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class DepartmentSerializer(serializers.ModelSerializer):
    parent_categories = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('id', 'name', 'parent_categories')

    def get_parent_categories(self, obj):
        categories = Category.objects.filter(categories__department__department=obj)
        parents = ParentCategory.objects.filter(childs__in=categories).distinct()
        return ParentCategorySerializer(parents, many=True).data


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
    brand_country = BrandCountry.objects.all().first()
    exchange = ExchangeRate.objects.all().first()
    x = round(price * brand_country.mark_up, brand_country.round_digit)
    return round(x * exchange.value)


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    brand = BrandSerializer()
    department = DepartmentsSerializer()
    category = CategorySerializer()
    colour = VendColourSerializer()

    class Meta:
        model = Product
        fields = ['discount_price', 'images', 'id',
                  'colour', 'created_at', 'title',
                  'original_price', 'updated_at', 'description',
                  'brand', 'department', 'category', 'colour']

    def get_images(self, obj):
        original = OriginalProduct.objects.get(link=obj.link)
        return original.images.split()

    def get_original_price(self, obj):
        # print(obj.link.url)
        return get_price(obj.link.originalproduct.original_price)

    def get_discount_price(self, obj):
        # print(obj.link.url)
        return get_price(obj.link.originalproduct.discount_price)
