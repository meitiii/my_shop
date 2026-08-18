from django.db import models
from django.conf import settings
from products.models import ProductVariant
from users.models import Address
from django.utils import timezone
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=0, help_text="درصد تخفیف (مثلا 10)")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="مبلغ ثابت تخفیف")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending','در انتظار پرداخت'),
        ('paid','پرداخت شده'),
        ('shipped','ارسال شده'),
        ('delivered','تحویل داده شده'),
        ('canceled','لغو شده')
    )
    PAYMENT_METHODS = (
        ('online', 'پرداخت اینترنتی'),
        ('cod', 'پرداخت درب منزل'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    total_price = models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True) 
    shipping_address = models.TextField(blank=True,null=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='online')
    delivery_date = models.DateField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
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
    