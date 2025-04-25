from django.db import models

# -------------------------
# 商店狀態
# -------------------------
class ShopState(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name 