from django.db import models
from goodBuy_shop.models import Product
from .order import Order

class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_price = models.IntegerField(null=True, blank=True)
    product_img = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product')
        ]
    
    def __str__(self):
        return self.product