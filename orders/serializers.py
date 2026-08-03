from rest_framework import serializers
from .models import OrderItem,Order
from products.serializers import ProductSerializer,ProductVariantSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only = True)

    class Meta:
        model = OrderItem
        fields = ['variant','price','quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,read_only=True)

    class Meta:
        model = Order
        fields = ['id','status','total_price','created_at','items']

