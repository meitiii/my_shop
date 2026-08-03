from django.db import models
from django.conf import settings
from products.models import Products

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='reviews')
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='reviews')

    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user','product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} Star"