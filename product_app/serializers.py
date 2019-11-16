from rest_framework import serializers

from product_app.models import Category, ParentCategory, Brand, Department, Slider, ImageSlider, Product, \
    OriginalProduct


# class RecursiveSerializer(serializers.Serializer):
#     def to_representation(self, value):
#         serializer = self.parent.parent.__class__(value, context=self.context)
#         return serializer.data


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


class DepartmentSerializer(serializers.ModelSerializer):
    parent_categories = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('id', 'name', 'parent_categories')

    def get_parent_categories(self, obj):
        categories = Category.objects.filter(trendyolcategory__department__department=obj)
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


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['selling_price', 'discount_price', 'images', 'id',
                  'colour', 'created_at', 'title',
                  'original_price', 'updated_at', 'description']

    def get_images(self, obj):
        original = OriginalProduct.objects.get(link=obj.link)
        return original.images.split()
