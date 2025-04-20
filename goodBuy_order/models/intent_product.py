from django.db import models
from .purchase_intent import *
from goodBuy_shop.models import Product

class IntentProduct(models.Model):
    intent = models.ForeignKey(PurchaseIntent, on_delete=models.CASCADE, related_name='intent_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('intent', 'product')
