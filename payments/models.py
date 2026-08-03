from django.db import models
from orders.models import OrderItem,Order

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('successful', 'موفق'),
        ('failed', 'ناموفق'),
    )

    order = models.OneToOneField(Order,on_delete=models.CASCADE,related_name='payment')
    amount = models.DecimalField(max_digits=12,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')

    authority = models.CharField(max_length=100,blank=True,null=True)
    ref_id = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - Order {self.order.id} - {self.status}"


