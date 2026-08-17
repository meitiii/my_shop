from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
from .models import Payment
from orders.models import Order
import uuid

class PaymentRequestView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status != 'pending':
            return Response({"error": "This order has already been paid or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        authority = str(uuid.uuid4())

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={'amount': order.total_price, 'authority': authority}
        )
        if not created:
            payment.authority = authority
            payment.save()

        verify_path = f"/api/payments/verify/?authority={payment.authority}"
        verify_url = request.build_absolute_uri(verify_path)

        return Response({
            "message": "You will be redirected to the payment gateway.",
            "payment_url": verify_url,
            "authority": payment.authority
        })


class PaymentVerifyView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        authority = request.query_params.get('authority')
        FRONTEND_URL = "http://localhost:8080/payment/verify" 
        
        if not authority:
            return redirect(f"{FRONTEND_URL}?status=failed&error=Authority parameter is missing.")

        payment = get_object_or_404(Payment, authority=authority)

        if payment.status == 'successful':
            return redirect(f"{FRONTEND_URL}?status=success&message=This payment has already been approved.")
        
        # شبیه‌سازی پرداخت موفق
        payment.status = 'successful'
        # 👈 کد پیگیری رو شبیه کدهای بانکی (حروف بزرگ) کردم
        payment.ref_id = str(uuid.uuid4().hex)[:10].upper() 
        payment.save()

        order = payment.order
        order.status = 'paid'
        order.save()

        return redirect(f"{FRONTEND_URL}?status=success&ref_id={payment.ref_id}&order_id={order.id}")