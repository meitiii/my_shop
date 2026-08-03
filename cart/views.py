from django.shortcuts import render
from .serializers import CartItemSerializer
from .models import CartItem,Cart
from rest_framework.response import Response
from rest_framework import viewsets,status


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer


    def get_queryset(self):
        cart,created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart = cart)

    def perform_create(self, serializer):
        cart,created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)