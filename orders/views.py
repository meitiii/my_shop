from django.shortcuts import render
from django.db import transaction
from rest_framework.response import Response
from .models import Order,OrderItem
from cart.models import Cart,CartItem
from rest_framework import viewsets,decorators,status
from .serializers import OrderItemSerializer,OrderSerializer
from decimal import Decimal
from users.models import Address
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    @decorators.action(detail=False, methods=['post'])
    def checkout(self, request):
        address_id = request.data.get('address_id')
        if not address_id:
            return Response({"error": "Please select a shipping address."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address selected."}, status=status.HTTP_400_BAD_REQUEST)

        address_snapshot = f"{address.receiver_name or request.user.username} | {address.receiver_phone or '-'} | {address.state or ''}, {address.city}, {address.full_address} | Postal Code: {address.postal_code}"

        with transaction.atomic():
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                return Response({"error": "Cart does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            cart_items = cart.item.all()

            if not cart_items.exists():
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(
                user=request.user,
                shipping_address=address_snapshot, 
                total_price=0
            )
            total = Decimal('0')

            for item in cart_items:
                variant = item.variant
                if variant.stock < item.quantity:
                    return Response({"error": f"{variant.product.name} inventory is not enough."}, status=status.HTTP_400_BAD_REQUEST)
                
                variant.stock -= item.quantity
                variant.save()
                
                OrderItem.objects.create(
                    order=order, 
                    variant=variant,
                    price=variant.price,
                    quantity=item.quantity
                )
                total += (variant.price * item.quantity)
            
            order.total_price = total
            order.save()
            
            cart.item.all().delete()
            
            return Response({
                "message": "Order successfully placed.",
                "order_id": order.id
            }, status=status.HTTP_201_CREATED)