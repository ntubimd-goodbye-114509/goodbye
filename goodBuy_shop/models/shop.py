from django.db import models
from goodBuy_web.models import User
from .permission import Permission
from .shop_state import ShopState
from .purchase_priority import PurchasePriority

# -------------------------
# 商店
# -------------------------
class ActiveShopManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(permission__id__in=[1, 2])  # 排除 permission_id=3（已刪除）

class Shop(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    introduce = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    shop_state = models.ForeignKey(ShopState, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    purchase_priority = models.ForeignKey(PurchasePriority, on_delete=models.CASCADE)
    
    transfer = models.BooleanField(default=False)
    deposit = models.BooleanField(default=False)
    deposit_ratio = models.PositiveIntegerField(default=50)
    update = models.DateTimeField(auto_now_add=True)
    
    is_rush_settled = models.BooleanField(default=False)
    objects = ActiveShopManager()
    
    def __str__(self):
        return self.name