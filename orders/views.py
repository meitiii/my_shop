from django.shortcuts import render
from django.db import transaction
from rest_framework.response import Response
from .models import Order,OrderItem
from cart.models import Cart,CartItem
from rest_framework import viewsets,decorators,status
from .serializers import OrderItemSerializer,OrderSerializer
from decimal import Decimal
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
            cart_items = cart.item.all()

            if not cart_items.exists():
                return Response({"error":"Cart is empty"},status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(user=request.user,total_price=0)
            total = Decimal('0')

            for item in cart_items:
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
            cart.item.all().delete()
            return Response({"message":"Order successfully placed.","order_id":order.id})






                
