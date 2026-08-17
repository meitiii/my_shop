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
from rest_framework.decorators import action


class ProductFilter(django_filters.FilterSet):
    brand = django_filters.BaseInFilter(
        field_name='brand',
        lookup_expr='in'
    )

    category = django_filters.NumberFilter(
        method='filter_category'
    )

    min_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='gte', distinct=True)
    max_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='lte', distinct=True)

    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')

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

        return queryset.filter(category_id__in=category_ids)

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__stock__gt=0).distinct()
        return queryset

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

    def filter_queryset(self, queryset):
     
        queryset = super().filter_queryset(queryset)
        
        spec_filters = {}
       
        feature_filters = self.request.query_params.getlist('feature')

        for key, value in self.request.query_params.items():
            if key.startswith('spec_'):
                spec_key = key.replace('spec_', '')
                spec_filters[f'technical_specs__{spec_key}__icontains'] = value
                
        if spec_filters:
            queryset = queryset.filter(**spec_filters)
      
        if feature_filters:
            for feat in feature_filters:
                queryset = queryset.filter(features__contains=[feat])
            
        return queryset

    
    @action(detail=False, methods=['get'])
    def available_filters(self, request):
        base_queryset = super().filter_queryset(self.get_queryset())
        
        specs_list = base_queryset.exclude(technical_specs__isnull=True)\
                                  .exclude(technical_specs={})\
                                  .values_list('technical_specs', flat=True)
                                  
        dynamic_filters = {}
        for specs in specs_list:
            if isinstance(specs, dict):
                for key, value in specs.items():
                    val_str = str(value).strip()
                    if not val_str:
                        continue
                    if key not in dynamic_filters:
                        dynamic_filters[key] = set()
                    dynamic_filters[key].add(val_str)
                    
        formatted_filters = {
            k: sorted(list(v)) for k, v in dynamic_filters.items()
        }

        features_list = base_queryset.exclude(features__isnull=True)\
                                     .exclude(features=[])\
                                     .values_list('features', flat=True)
        
        unique_features = set()
        for feats in features_list:
            if isinstance(feats, list): 
                for f in feats:
                    val_str = str(f).strip()
                    if val_str:
                        unique_features.add(val_str)
        
        if unique_features:
            formatted_filters['Special Features'] = sorted(list(unique_features))
            
        return Response(formatted_filters)
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


