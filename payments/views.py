from django.shortcuts import render
from .models import Payment
from orders.models import Order,OrderItem
from rest_framework import views,status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.shortcuts import get_list_or_404,get_object_or_404,redirect
import uuid


class PaymentRequestView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,order_id):
        order = get_object_or_404(Order,id = order_id,user=request.user)
        if order.status!='pending':
            return Response({"error":"This order has already paid for or is invalid."},status=status.HTTP_400_BAD_REQUEST)

        authority = str(uuid.uuid4())

        payment,created = Payment.objects.get_or_create(order=order,defaults=
                                                        {'amount':order.total_price,
                                                         'authority':authority})
        if not created:
            payment.authority = authority
            payment.save()

        verify_url = f"http://127.0.0.1:8000/api/payments/verify/?authority={payment.authority}"

        return Response({
            "message":"You will be redirected to the payment gateway.",
            "payment_url":verify_url,
            "authority":payment.authority
        })


class PaymentVerifyView(views.APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        authority = request.query_params.get('authority')
        FRONTEND_URL = "http://localhost:5173/payment/verify"
        if not authority:
            return Response({"error":"The authority parameter is required."},status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(Payment,authority=authority)

        if payment.status=='successful':
            return redirect(f"{FRONTEND_URL}?status=success&message=This payment has already been approved.")
        payment.status = 'successful'
        payment.ref_id = str(uuid.uuid4().hex)[:10]
        payment.save()

        order = payment.order
        order.status = 'paid'
        order.save()

        return redirect(f"{FRONTEND_URL}?status=success&ref_id={payment.ref_id}&order_id={order.id}")
        