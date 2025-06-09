from django.db import models
from goodBuy_web.models import User
from .shop import Shop

# -------------------------
# 商店足跡
# -------------------------
class ShopFootprints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'shop'], name='unique_user_shop_footprints'),
            models.UniqueConstraint(fields=['session_key', 'shop'], name='unique_session_shop_footprints'),
        ]

    def __str__(self):
        identifier = self.user.username if self.user else f"匿名-{self.session_key}"
        return f"{identifier} - {self.shop.name}"
