from rest_framework import serializers

from product_app.models import Category, Department, Link, OriginalProduct, Product, ParentCategory, Country, \
    BrandCountry

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


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentCategory
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    parent = ParentSerializer()

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


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
        fields = ('id', 'name', 'is_active', 'link', 'created_at', 'updated_at', 'project', 'countries', 'currency')

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


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class CategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class BrandItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class IziProductSerializer(serializers.ModelSerializer):
    brand = BrandItemSerializer()
    category = CategoryItemSerializer()
    department = DepartmentSerializer()

    class Meta:
        model = Product
        fields = ['selling_price', 'discount_price', 'id', 'link', 'brand', 'category', 'department',
                  'colour', 'created_at', 'title',
                  'original_price', 'updated_at', 'description']


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


class ProductSerializer(serializers.ModelSerializer):
    link = LinkSerializer()
    images = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = OriginalProduct
        fields = ['selling_price', 'discount_price', 'is_free_argo', 'images', 'delivery_date', 'product_code', 'id',
                  'colour', 'promotions', 'created_at', 'active', 'product_id', 'link', 'is_rush_delivery', 'title',
                  'original_price', 'updated_at', 'description', 'product']

    def get_images(self, obj):
        return obj.images.split()

    def get_product(self, obj):
        product = Product.objects.get(link=obj.link)
        return IziProductSerializer(product).data
