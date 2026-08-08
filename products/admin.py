from django.contrib import admin

from .models import Category, ProductVariant, Products, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {
        'slug': ('name',)
    }


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'sku',
        'category',
        'brand',
        'created_at',
        'is_active',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    list_filter = (
        'category',
        'brand',
        'is_active',
    )

    search_fields = [
        'name',
        'sku',
        'brand',
    ]

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]

    fieldsets = [
        (
            'Basic Information',
            {
                'fields': (
                    'name',
                    'slug',
                    'sku',
                    'category',
                    'brand',
                    'is_active',
                )
            }
        ),
        (
            'Descriptions',
            {
                'fields': (
                    'short_description',
                    'description',
                )
            }
        ),
        (
            'Specifications and features',
            {
                'fields': (
                    'features',
                    'technical_specs',
                )
            }
        ),
        (
            'Size and warranty',
            {
                'fields': (
                    'weight',
                    'dimensions',
                    'material',
                    'warranty',
                    'country_of_origin',
                )
            }
        ),
    ]