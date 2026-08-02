from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email  = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11,blank=True,null=True)

    USERNAME_FIELD ='email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username