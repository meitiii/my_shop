from django.contrib import admin

from .models import Category,ProductVariant,Products,ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','parent')
    prepopulated_fields = {'slug':('name',)}


class ProdectImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProdectVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name','category','brand','created_at')
    prepopulated_fields = {'slug':('name',)}
    list_filter = ('category','brand')
    search_fields = ('name','description')
    inlines = [ProdectImageInline,ProdectVariantInline]
