from rest_framework import serializers
from .models import Category, ProductImage, ProductVariant, Products,Brand,HeroSlider


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image','parent','subcategories']

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','product', 'image', 'alt_text', 'is_main', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','product', 'color', 'size', 'price', 'stock','discount_percent']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'image']
class ProductSerializer(serializers.ModelSerializer):

    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = CategorySerializer(read_only=True)

   
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )

    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    average_rating = serializers.FloatField(read_only=True)

    thumbnail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Products
        fields = '__all__'

    def get_thumbnail(self, obj):
        main_image = obj.images.filter(is_main=True).first()

        if main_image and main_image.image:
            request = self.context.get('request')

            if request:
                return request.build_absolute_uri(main_image.image.url)

            return main_image.image.url

        first_image = obj.images.first()

        if first_image and first_image.image:
            request = self.context.get('request')

            if request:
                return request.build_absolute_uri(first_image.image.url)

            return first_image.image.url

        return None



class HeroSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlider
        fields = '__all__'

