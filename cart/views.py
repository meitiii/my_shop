from django.shortcuts import render
from .serializers import CartItemSerializer
from .models import CartItem,Cart
from rest_framework.response import Response
from rest_framework import viewsets,status
from products.models import ProductVariant
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]



    def get_queryset(self):
        cart,created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart = cart)
    
    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        variant_id = request.data.get('variant')
        quantity = int(request.data.get('quantity', 1))

        variant = get_object_or_404(ProductVariant, id=variant_id)

        if variant.stock < quantity:
            return Response({'error': 'Not enough stock available.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, is_created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        
        if not is_created:
            if variant.stock < (cart_item.quantity + quantity):
                return Response({'error': 'Cannot add more. Not enough stock.'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        new_quantity = int(request.data.get('quantity', instance.quantity))

        if instance.variant.stock < new_quantity:
            return Response({'error': 'Requested quantity exceeds stock.'}, status=status.HTTP_400_BAD_REQUEST)

        instance.quantity = new_quantity
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)