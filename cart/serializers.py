from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.ReadOnlyField(source='variant.__str__')
    price = serializers.ReadOnlyField(source='variant.price')
    stock = serializers.ReadOnlyField(source='variant.stock')
    image = serializers.SerializerMethodField()
    product_id = serializers.ReadOnlyField(source='variant.product.id')

    class Meta:
        model = CartItem
        fields = ['id','variant','quantity','variant_name','price','stock', 'image', 'product_id']

    def get_image(self,obj):
        main_image = obj.variant.product.images.filter(is_main = True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
            return main_image.image.url
        return None

