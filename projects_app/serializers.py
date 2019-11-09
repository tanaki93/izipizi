from rest_framework import serializers

from product_app.models import Category, Department, Link

# class RecursiveSerializer(serializers.Serializer):
#     def to_representation(self, value):
#         serializer = self.parent.parent.__class__(value, context=self.context)
#         return serializer.data
from product_app.models import Brand, TrendYolCategory, TrendYolDepartment


class TrendYolDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendYolDepartment
        fields = ('id', 'name')


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)


class TrendYolCategoryDetailedSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = TrendYolCategory
        fields = ('id', 'name', 'link', 'is_active', 'category')


class TrendYolCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendYolCategory
        fields = ('id', 'name', 'is_active')


class BrandSerializer(serializers.ModelSerializer):
    categories_count = serializers.SerializerMethodField()
    departments_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'is_active', 'link', 'created_at', 'updated_at', 'is_trend_yol', 'categories_count',
                  'departments_count')

    def get_departments_count(self, obj):
        departments = TrendYolDepartment.objects.filter(brand=obj).count()
        return departments

    def get_categories_count(self, obj):
        categories = TrendYolCategory.objects.filter(department__brand=obj).count()
        return categories


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class TrendYolDepartmentDetailedSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = TrendYolDepartment
        fields = ('id', 'name', 'department', 'is_active', 'categories')

    def get_categories(self, obj):
        categories = TrendYolCategory.objects.filter(department=obj)
        return TrendYolCategoryDetailedSerializer(categories, many=True).data


class BrandDetailedSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'is_active', 'departments')

    def get_departments(self, obj):
        departments = TrendYolDepartment.objects.filter(brand=obj)
        return TrendYolDepartmentDetailedSerializer(departments, many=True).data
