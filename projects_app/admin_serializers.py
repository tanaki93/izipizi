from rest_framework import serializers

from product_app.models import Brand, TrendYolDepartment, TrendYolCategory, Link, Document
from user_app.serializers import UserSerializer


class TrendYolCategoryDetailedSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = TrendYolCategory
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
        model = TrendYolDepartment
        fields = ('id', 'name', 'is_active', 'categories')

    def get_categories(self, obj):
        categories = TrendYolCategory.objects.filter(department=obj)
        return TrendYolCategoryDetailedSerializer(categories, many=True).data


class BrandAdminDetailedSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'is_active', 'departments')

    def get_departments(self, obj):
        departments = TrendYolDepartment.objects.filter(brand=obj)
        return TrendYolDepartmentDetailedSerializer(departments, many=True).data


class DocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Document
        fields = ('id', 'updated_at', 'user', 'status')
