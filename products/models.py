from django.db import models
from django.contrib.auth.models import AbstractUser
from  PIL import Image
import io
from django.core.files.base import ContentFile

class Brand(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True,allow_unicode=True)
    image = models.ImageField(upload_to='brands/images/', blank=True, null=True, help_text="Brand logo")


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, allow_unicode= True)

    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='subcategories')
    #image
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True, help_text="Category image")


    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name

class Products(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True,allow_unicode=True)
    description = models.TextField()
    category =models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True,blank=True,related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    sku = models.CharField(max_length=100,unique=True,help_text='unique product code')
    short_description = models.CharField(max_length=500,blank=True)

    features = models.JSONField(default=list,blank=True,help_text="List of key features such as: ['waterproof', 'powerful battery']")
    technical_specs  = models.JSONField(default=dict,blank=True,help_text= "Technical specifications such as: {'Weight': '200g', 'Dimensions': '10x5'}")
    
    weight = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,help_text=
                                'Weight in kilograms')
    dimensions  = models.CharField(max_length=100,blank=True,null=True,help_text='For example 10x20x30 cm')
    material = models.CharField(max_length=100,blank=True,null=True)
    warranty =models.CharField(max_length=255,blank=True,null=True)
    country_of_origin = models.CharField(max_length=100,blank=True,null=True)

    is_active = models.BooleanField(default=True,help_text='Product active/inactive status')


    views_count = models.PositiveIntegerField(default=0, help_text=' Number of view')
    sales_count = models.PositiveIntegerField(default=0, help_text='Number of sale')
    is_featured = models.BooleanField(default=False, help_text='Selected product')
    

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='variants')
    size = models.CharField(max_length=50,blank=True,null=True)
    color = models.CharField(max_length=50,blank=True,null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    discount_percent = models.PositiveIntegerField(default=0, help_text="Discount percentage (0-100)")
    

    def __str__(self):
        return f"{self.product.name} - {self.color or ''} {self.size or ''}"

class ProductImage(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=100,blank=True,null=True)


    is_main = models.BooleanField(default=False,help_text='Is this the main image (Thumbnail) of the product?')
    order = models.PositiveIntegerField(default=0,help_text='Order of displaying photos')
    class Meta:
        ordering = ['order']

    def __str__(self):

        return f"Image for {self.product.name}"

    def save(self, *args,**kwargs):
        if self.image:
            if not self.image.name.endswith('.webp'):
                img = Image.open(self.image)
                img_io = io.BytesIO()

                if img.mode in ["RGBA","p"]:
                    img = img.convert("RGB")

                img.save(img_io,format='WEBP',quality=80)
                new_filename = f"{self.image.name.split('.')[0]}.webp"
                self.image.save(new_filename,ContentFile(img_io.getvalue()),save=False)

            if self.is_main:
                ProductImage.objects.filter(product = self.product).update(is_main = False)

            super().save(*args, **kwargs)


class HeroSlider(models.Model):
    title = models.CharField(max_length=100, help_text="Example: Galaxy S24 Ultra")
    subtitle = models.CharField(max_length=100, blank=True, help_text="Small text above the title")
    description = models.TextField(blank=True, help_text="Description under the title")
    image = models.ImageField(upload_to='sliders/')
    button_text = models.CharField(max_length=50, default="Shop Now")
    button_link = models.CharField(max_length=255, default="/", help_text="Button link (example: /product/1)")
    
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title