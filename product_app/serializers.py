from rest_framework import serializers

from product_app.models import Category


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    category_set = RecursiveSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'parent', 'name', 'category_set')
