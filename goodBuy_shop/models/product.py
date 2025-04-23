from django.db import models
from .shop import Shop
import os
from django.conf import settings

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    stock = models.IntegerField()
    amount = models.IntegerField()
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='product_img/', blank=True, null=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name