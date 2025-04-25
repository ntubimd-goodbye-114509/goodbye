from django.db import models
from goodBuy_shop.models import Product
from goodBuy_web.models import User
from django.db.models import Sum

# -------------------------
# 購物車
# -------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    update = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_cart')
        ]

    # -------------------------
    # 商品已存在則修改數量
    # -------------------------
    def add_or_update_product(self, product, quantity):
        try:
            obj = Cart.objects.get(user=self.user, product=product)
            obj.amount = min(obj.amount + quantity, product.stock)
        except Cart.DoesNotExist:
            obj = Cart(user=self.user, product=product, amount=min(quantity, product.stock))

        obj.save()
        return obj

    
    def __str__(self):
        return f'{self.product}*{self.amount}'