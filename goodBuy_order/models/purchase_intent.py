from django.db import models
from goodBuy_web.models import User
from goodBuy_shop.models import Shop

class PurchaseIntent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} 對 {self.shop} 多帶'