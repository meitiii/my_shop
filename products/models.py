from django.db import models
from django.contrib.auth.models import AbstractUser


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, allow_unicode= True)

    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='children')

    def __str__(self):
        return self.name

class Products(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True,allow_unicode=True)
    description = models.TextField()
    category =models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
    brand = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='variants')
    size = models.CharField(max_length=50,blank=True,null=True)
    color = models.CharField(max_length=50,blank=True,null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.color or ''} {self.size or ''}"

class ProductImage(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return f"Image for {self.product.name}"

