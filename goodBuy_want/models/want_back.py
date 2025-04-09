from django.db import models
from goodBuy_shop.models import Shop
from goodBuy_web.models import User
from .want import Want

class WantBack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    want = models.ForeignKey(Want, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)