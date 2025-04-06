from django.db import models
from goodBuy_web.models import User
from .shop import Shop

class ShopFootprints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)