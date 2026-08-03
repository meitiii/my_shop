from django.urls import path,include
from .views import PaymentVerifyView,PaymentRequestView


urlpatterns = [
    path('request/<int:order_id>/',PaymentRequestView.as_view(),name='payment_request'),
    path('verify/',PaymentVerifyView.as_view(),name='payment_verify'),
    
]