from rest_framework import serializers
from .models import Category, ProductImage, ProductVariant, Products


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_main', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size', 'price', 'stock']


class ProductSerializer(serializers.ModelSerializer):

    
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
        fields = [
            'id',
            'name',
            'slug',
            'description',

            # GET
            'category',

            # POST / PATCH
            'category_id',

            'brand',
            'created_at',
            'updated_at',
            'average_rating',
            'images',
            'variants',
            'sku',
            'short_description',
            'features',
            'technical_specs',
            'weight',
            'dimensions',
            'material',
            'warranty',
            'country_of_origin',
            'is_active',
            'thumbnail',
        ]

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

