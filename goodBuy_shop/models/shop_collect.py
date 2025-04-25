from django.db import models
from goodBuy_web.models import User
from .shop import Shop

# -------------------------
# 商店收藏
# -------------------------
class ShopCollect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'shop'], name='unique_user_shop_collect')
        ]
    
    def __str__(self):
        return self.shop