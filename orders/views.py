from django.db import transaction
from rest_framework.response import Response
from rest_framework import viewsets, decorators, status
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem, Coupon
from cart.models import Cart
from users.models import Address
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    @decorators.action(detail=False, methods=['post'])
    def validate_coupon(self, request):
        code = request.data.get('code')
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                return Response({
                    "discount_percent": coupon.discount_percent,
                    "discount_amount": coupon.discount_amount
                })
            else:
                return Response({"error": "This coupon is expired or inactive."}, status=400)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon code."}, status=400)

    @decorators.action(detail=False, methods=['post'])
    def checkout(self, request):
        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method', 'online')
        delivery_date = request.data.get('delivery_date') # فرمت YYYY-MM-DD
        coupon_code = request.data.get('coupon_code')
        
        if not address_id or not delivery_date:
            return Response({"error": "Address and delivery date are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address selected."}, status=status.HTTP_400_BAD_REQUEST)

        address_snapshot = f"{address.receiver_name or request.user.username} | {address.receiver_phone or '-'} | {address.state or ''}, {address.city}, {address.full_address} | Postal Code: {address.postal_code}"

        applied_coupon = None
        if coupon_code:
            try:
                applied_coupon = Coupon.objects.get(code=coupon_code)
                if not applied_coupon.is_valid():
                    applied_coupon = None
            except Coupon.DoesNotExist:
                applied_coupon = None

        with transaction.atomic():
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                return Response({"error": "Cart does not exist"}, status=400)
            
            cart_items = cart.item.all()
            if not cart_items.exists():
                return Response({"error": "Cart is empty"}, status=400)

            order = Order.objects.create(
                user=request.user,
                shipping_address=address_snapshot,
                payment_method=payment_method,
                delivery_date=delivery_date,
                coupon=applied_coupon,
                total_price=0
            )
            
            items_total = Decimal('0')

            for item in cart_items:
                variant = item.variant
                if variant.stock < item.quantity:
                    return Response({"error": f"{variant.product.name} out of stock."}, status=400)
                
                item_price = variant.price
                if variant.discount_percent > 0:
                    discount = (item_price * Decimal(variant.discount_percent)) / Decimal(100)
                    item_price = item_price - discount
                
                variant.stock -= item.quantity
                variant.save()
                
                OrderItem.objects.create(
                    order=order, 
                    variant=variant,
                    price=item_price,
                    quantity=item.quantity
                )
                items_total += (item_price * item.quantity)
            
            coupon_discount_amount = Decimal('0')
            if applied_coupon:
                if applied_coupon.discount_percent > 0:
                    coupon_discount_amount = (items_total * Decimal(applied_coupon.discount_percent)) / Decimal(100)
                elif applied_coupon.discount_amount > 0:
                    coupon_discount_amount = applied_coupon.discount_amount
            
            shipping_cost = Decimal('15.00')
            
            final_total = (items_total - coupon_discount_amount) + shipping_cost
            if final_total < 0:
                final_total = Decimal('0')

            order.shipping_cost = shipping_cost
            order.discount_amount = coupon_discount_amount
            order.total_price = final_total
            order.save()
            
            cart.item.all().delete()
            
            return Response({
                "message": "Order successfully placed.",
                "order_id": order.id,
                "payment_method": payment_method
            }, status=status.HTTP_201_CREATED)