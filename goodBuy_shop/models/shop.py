from django.db import models
from goodBuy_web.models import User
from .permission import Permission
from .shop_state import ShopState
from .purchase_priority import PurchasePriority



class Shop(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    introduce = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    shop_state = models.ForeignKey(ShopState, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    purchase_priority = models.ForeignKey(PurchasePriority, on_delete=models.CASCADE)
    deposit = models.BooleanField(default=False)
    deposit_ratio = models.PositiveIntegerField(default=50)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name