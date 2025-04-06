from django.db import models
from .shop import Shop

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    amount = models.IntegerField()
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='product_img/', blank=True, null=True)

    def __str__(self):
        return self.name