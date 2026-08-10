from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,CategoryViewSet,ProductImageViewSet,ProductVariantViewSet


router = DefaultRouter()
router.register(r'categories',CategoryViewSet,basename='category')
router.register(r'products',ProductViewSet,basename='product')
router.register(r'product-images',ProductImageViewSet,basename='product-image')
router.register(r'product-variants',ProductVariantViewSet,basename='product-variant')
urlpatterns = [
    path('',include(router.urls))
]