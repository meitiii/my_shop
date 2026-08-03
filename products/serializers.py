from rest_framework import serializers
from .models import Category,ProductImage,ProductVariant,Products


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug','parent']



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image','alt_text']



class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','color','size','price','stock']



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True,read_only=True)
    variants = ProductVariantSerializer(many=True,read_only= True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.FloatField(read_only =True)

    class Meta:
        model = Products
        fields = ['id','name','slug','description',
                  'category','brand','created_at',
                  'updated_at',"average_rating"
                  ,'images','variants']