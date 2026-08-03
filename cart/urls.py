from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

router = DefaultRouter()
router.register(r'items',CartViewSet,basename='cart-item')
urlpatterns = [
    path('',include(router.urls))
]