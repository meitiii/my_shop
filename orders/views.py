from django.shortcuts import render
from django.db import transaction
from rest_framework.response import Response
from .models import Order,OrderItem
from cart.models import Cart,CartItem
from rest_framework import viewsets,decorators,status
from .serializers import OrderItemSerializer,OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user = self.request.user)

    @decorators.action(detail=False,methods=['post'])
    def checkout(self,request):
        with transaction.atomic():
            try:
                cart = Cart.objects.get(user = request.user)
            except Cart.DoesNotExist:
                return Response({"error":"Cart dose not exist"},status=status.HTTP_400_BAD_REQUEST)
            cart_item = Cart.items.all()

            if not cart_item.exists():
                return Response({"error":"Cart is empty"},status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(user=request.user,total_price=0)
            total = 0

            for item in cart_item:
                variant = item.variant
                if variant.stock < item.quantity:
                    return Response({"error":f"{variant.product.name} inventory is not enough."},status=400)
                variant.stock-=item.quantity
                variant.save()
                OrderItem.objects.create(order=order,variant=variant,
                                     price = variant.price,
                                     quantity=item.quantity)
                total+=(variant.price*item.quantity)
            order.total_price = total
            order.save()
            cart.items.all().delete()
            return Response({"message":"Order successfully placed.","order_id":order.id})






                
