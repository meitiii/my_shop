from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id','user_name','product','rating','comment','created_at','is_approved']
        read_only_fields = ['id','is_approved']

