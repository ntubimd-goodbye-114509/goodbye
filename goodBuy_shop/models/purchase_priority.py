from django.db import models

# -------------------------
# 購買制度
# 時間、金額、數量
# -------------------------
class PurchasePriority(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name 