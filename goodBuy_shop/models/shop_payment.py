from django.db import models
from .shop import Shop
from goodBuy_web.models import Payment_Account

class ShopPayment(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    payment_account = models.ForeignKey(Payment_Account, on_delete=models.CASCADE)