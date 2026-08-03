from django.shortcuts import render
from .serializers import ReviewSerializer
from rest_framework.response import Response
from rest_framework import viewsets,status,permissions
from .models import Review
from orders.models import OrderItem


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(is_approved = True)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        user = request.user

        has_purchesed = OrderItem.objects.filter(
            order__user =user,
            order_status = 'paid',
            variant__product_id=product_id
        ).exists()

        if not has_purchesed:
            return Response({"error":"You can only leave a review for products you have purchased."}
                            ,status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)


        return Response({
            "message":"Your comment has been successfully submitted and will be displayed after approval by the administration."
        },status=status.HTTP_201_CREATED)
        
        
