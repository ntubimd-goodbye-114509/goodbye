from django.db import models
from .purchase_intent import *
from goodBuy_shop.models import Product
from django.db.models import Sum


class IntentProduct(models.Model):
    intent = models.ForeignKey(PurchaseIntent, on_delete=models.CASCADE, related_name='intent_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('intent', 'product')

    def add_or_update_product(self, product, quantity):
        obj, created = IntentProduct.objects.get_or_create(intent=self, product=product)

        current_total = IntentProduct.objects.filter(product=product).exclude(id=obj.id).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        available_qty = max(product.stock - current_total, 0)

        if created:
            obj.quantity = min(quantity, available_qty)
        else:
            obj.quantity = min(obj.quantity + quantity, available_qty)

        obj.save()
        return obj