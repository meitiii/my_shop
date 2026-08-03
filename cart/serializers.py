from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.ReadOnlyField(source='variant.__str__')
    price = serializers.ReadOnlyField(source='variant.price')

    class Meta:
        model = CartItem
        fields = ['id','variant','quantity','variant_name','price']

