from django.db import models
from .purchase_intent import *
from goodBuy_shop.models import Product

class IntentProduct(models.Model):
    intent = models.ForeignKey(PurchaseIntent, on_delete=models.CASCADE, related_name='intent_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('intent', 'product')

    def add_or_update_product(self, product, quantity):
        intent_product, created = IntentProduct.objects.get_or_create(
            intent=self,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            intent_product.quantity += quantity
            intent_product.save()
        return intent_product, created
