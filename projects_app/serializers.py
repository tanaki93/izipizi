from rest_framework import serializers

from product_app.models import Category

# class RecursiveSerializer(serializers.Serializer):
#     def to_representation(self, value):
#         serializer = self.parent.parent.__class__(value, context=self.context)
#         return serializer.data
from projects_app.models import Brand, TrendYolCategory, TrendYolDepartment


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')


class TrendYolDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendYolDepartment
        fields = ('id', 'name')


class TrendYolCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendYolCategory
        fields = ('id', 'name')
