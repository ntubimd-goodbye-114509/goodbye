from django.db import models
from goodBuy_shop.models import Product
from .order import Order

# -------------------------
# 訂單商品
# -------------------------
class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product')
        ]
    
    def __str__(self):
        return self.product