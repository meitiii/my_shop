from django.shortcuts import render
from rest_framework import viewsets,filters
from rest_framework.permissions import AllowAny
from .models import Products,Category,ProductVariant,ProductImage
from .serializers import ProductSerializer,CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
 

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = Products.objects.all().order_by('-created_at')
    queryset = Products.objects.annotate(average_rating=Avg('reviews__rating')).order_by('-created_at')

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['category','brand']
    search_fields = ['name','description']
    ordering_fields = ['created_at','name']


