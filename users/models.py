from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email  = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11,blank=True,null=True)

    USERNAME_FIELD ='email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username



class Address(models.Model):    
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='addresses')
    title = models.CharField(max_length=50,help_text='For example: home, workplace')
    state = models.CharField(max_length=50,blank=True,null=True)
    city = models.CharField(max_length=50)
    full_address = models.TextField(max_length=500)
    postal_code = models.CharField(max_length=10)
    receiver_name = models.CharField(max_length=100,blank=True,null=True,help_text="Delivery recipient-name")
    receiver_phone =models.CharField(max_length=11,blank=True,null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def save(self,*args, **kwargs):
        if self.is_default:
            Address.objects.filter(user = self.user).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.user.username}"




