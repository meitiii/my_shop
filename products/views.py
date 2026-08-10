from django.shortcuts import render
from rest_framework import viewsets,filters
from rest_framework.permissions import AllowAny
from .models import Products,Category,ProductVariant,ProductImage
from .serializers import ProductSerializer,CategorySerializer,ProductImageSerializer,ProductVariantSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg,Q
from .permissions import IsAdminOrReadOnly
from rest_framework.viewsets import ModelViewSet


class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductVariantViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
 

class ProductViewSet(ModelViewSet):
    #queryset = Products.objects.all().order_by('-created_at')
    queryset = Products.objects.annotate(average_rating=Avg('reviews__rating',filter=Q(reviews__is_approved=True))).order_by('-created_at')

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['category','brand','is_active']
    search_fields = ['name','description','slug','sku']
    ordering_fields = ['price','created_at']


