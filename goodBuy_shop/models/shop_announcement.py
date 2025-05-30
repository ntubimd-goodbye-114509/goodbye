from django.db import models
from .shop import Shop

# -------------------------
# 商店公告
# -------------------------
class ShopAnnouncement(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    announcement = models.TextField(blank=True, null=True)
    update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title