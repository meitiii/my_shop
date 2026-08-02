from django.db import models
from django.conf import settings
from products.models import ProductVariant


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending','در انتظار پرداخت'),
        ('paid','پرداخت شده'),
        ('shipped','ارسال شده'),
        ('delivered','تحویل داده شده'),
        ('canceled','لغو شده')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='orders')
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    total_price = models.DecimalField(max_digits=12,decimal_places=2,default=0.00)

    shipping_address = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    variant = models.ForeignKey(ProductVariant,on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.variant} for Order {self.order.id}"
    