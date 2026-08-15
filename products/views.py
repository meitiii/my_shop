from django.shortcuts import render
from rest_framework import viewsets,filters
from rest_framework.permissions import AllowAny
from .models import Products,Category,ProductVariant,ProductImage,Brand,HeroSlider
from .serializers import ProductSerializer,CategorySerializer,ProductImageSerializer,ProductVariantSerializer,BrandSerializer,HeroSliderSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg,Q,Min
from .permissions import IsAdminOrReadOnly
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as django_filters
from rest_framework.response import Response
class ProductFilter(django_filters.FilterSet):

    brand = django_filters.BaseInFilter(
        field_name='brand',
        lookup_expr='in'
    )

    category = django_filters.NumberFilter(
        method='filter_category'
    )

    def filter_category(self, queryset, name, value):
        
        if not value:
            return queryset

        try:
            category = Category.objects.get(id=value)
        except Category.DoesNotExist:
            return queryset.none()

        category_ids = [category.id]

        def collect_children(parent_id):
            children = Category.objects.filter(parent_id=parent_id)

            for child in children:
                category_ids.append(child.id)
                collect_children(child.id)

        collect_children(category.id)

        return queryset.filter(
            category_id__in=category_ids
        )

    class Meta:
        model = Products
        fields = ['category', 'brand', 'is_active']
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
 
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
class ProductViewSet(ModelViewSet):
    #queryset = Products.objects.all().order_by('-created_at')
    queryset = Products.objects.annotate(
    average_rating=Avg(
        'reviews__rating',
        filter=Q(reviews__is_approved=True)
    ),
    min_price=Min('variants__price')
)

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'slug', 'sku', 'brand__name', 'category__name']
    ordering_fields = [       
        'min_price',       
        'created_at',      
        'sales_count',     
        'views_count',     
        'average_rating',  
        'is_featured'      
    ]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()    
        instance.views_count +=1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class HeroSliderViewSet(viewsets.ModelViewSet):
    serializer_class = HeroSliderSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return HeroSlider.objects.all().order_by('order')
        return HeroSlider.objects.filter(is_active=True).order_by('order')


