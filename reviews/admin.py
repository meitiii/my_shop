from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'rating',
        'is_approved',
        'created_at'
    )
    list_filter = (
        'is_approved',
        'rating'
    )
    search_fields = (
        'user__username',
        'product__name',
        'comment'
    )