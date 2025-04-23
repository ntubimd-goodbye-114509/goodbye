from django.db import models
from .shop import Shop
import os
from django.conf import settings

class ActiveProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    stock = models.IntegerField()
    amount = models.IntegerField()
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='product_img/', blank=True, null=True)
    is_delete = models.BooleanField(default=False)

    objects = ActiveProductManager() 

    def __str__(self):
        return self.name