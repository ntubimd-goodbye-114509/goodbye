from django.db import models
from goodBuy_shop.models import Product
from goodBuy_web.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    update = models.DateTimeField(auto_now_add=True)